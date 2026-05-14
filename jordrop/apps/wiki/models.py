import bleach
import markdown as md
from django.conf import settings
from django.db import models, transaction
from apps.core.models import TimeStampedModel
from apps.games.models import Game


def render_markdown(content):
    """Convert Markdown to sanitised HTML. Called before storing content_rendered."""
    raw_html = md.markdown(
        content,
        extensions=['fenced_code', 'tables', 'toc', 'nl2br'],
    )
    allowed_tags = getattr(settings, 'BLEACH_ALLOWED_TAGS', bleach.sanitizer.ALLOWED_TAGS)
    allowed_attrs = getattr(settings, 'BLEACH_ALLOWED_ATTRS', bleach.sanitizer.ALLOWED_ATTRIBUTES)
    return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs)


class Page(TimeStampedModel):
    """
    The canonical wiki page. Stores ONLY metadata — content lives in PageRevision.
    current_revision points to the live revision shown to visitors.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    current_revision = models.OneToOneField(
        'PageRevision',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = ('game', 'slug')
        ordering = ['title']

    def __str__(self):
        return f'{self.game.name} / {self.title}'

    def get_absolute_url(self):
        return f'/wiki/{self.game.slug}/{self.slug}/'

    def apply_revision(self, revision):
        """Atomically promote a PageRevision to be the live version."""
        self.current_revision = revision
        self.is_published = True
        self.save(update_fields=['current_revision', 'is_published', 'updated_at'])


class PageRevision(TimeStampedModel):
    """
    Immutable snapshot. One row is inserted per save; rows are never updated.
    Restoring an old version = calling page.apply_revision(old_revision).
    """
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='revisions')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='revisions',
    )
    content = models.TextField()           # Raw Markdown source
    content_rendered = models.TextField()  # Pre-rendered + bleach-sanitised HTML
    edit_summary = models.CharField(max_length=300, blank=True)
    revision_number = models.PositiveIntegerField(editable=False)

    class Meta:
        unique_together = ('page', 'revision_number')
        ordering = ['-revision_number']

    def __str__(self):
        return f'{self.page.title} — rev {self.revision_number}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on INSERT
            last = self.page.revisions.order_by('-revision_number').first()
            self.revision_number = (last.revision_number + 1) if last else 1
            if not self.content_rendered:
                self.content_rendered = render_markdown(self.content)
        super().save(*args, **kwargs)


class EditRequest(TimeStampedModel):
    """
    A contributor's proposed change to a page, awaiting moderator review.
    Workflow: contributor submits → status=pending → moderator approves/rejects.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='edit_requests')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='edit_requests',
    )
    proposed_content = models.TextField()
    edit_summary = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_edits',
    )
    review_comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'EditRequest #{self.pk} on {self.page.title} by {self.author}'

    def approve(self, moderator):
        """
        Create a new PageRevision from proposed_content and promote it.
        Wrapped in a transaction so partial failures leave no inconsistent state.
        """
        with transaction.atomic():
            revision = PageRevision.objects.create(
                page=self.page,
                author=self.author,
                content=self.proposed_content,
                edit_summary=self.edit_summary,
            )
            self.page.apply_revision(revision)
            self.status = self.STATUS_APPROVED
            self.reviewed_by = moderator
            self.save(update_fields=['status', 'reviewed_by', 'updated_at'])
        return revision

    def reject(self, moderator, comment=''):
        self.status = self.STATUS_REJECTED
        self.reviewed_by = moderator
        self.review_comment = comment
        self.save(update_fields=['status', 'reviewed_by', 'review_comment', 'updated_at'])

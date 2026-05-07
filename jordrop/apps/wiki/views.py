import difflib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.decorators import contributor_required, moderator_required
from .forms import EditRequestForm, PageForm
from .models import EditRequest, Page, PageRevision
from apps.games.models import Game


# ── Public views ──────────────────────────────────────────────────────────────

def wiki_list(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    pages = game.pages.filter(is_published=True).select_related('current_revision')
    return render(request, 'wiki/list.html', {'game': game, 'pages': pages})


def page_detail(request, game_slug, slug):
    game = get_object_or_404(Game, slug=game_slug)
    page = get_object_or_404(Page, game=game, slug=slug, is_published=True)
    revision = page.current_revision
    return render(request, 'wiki/detail.html', {
        'game': game, 'page': page, 'revision': revision,
    })


def page_history(request, game_slug, slug):
    game = get_object_or_404(Game, slug=game_slug)
    page = get_object_or_404(Page, game=game, slug=slug, is_published=True)
    revisions = page.revisions.select_related('author').all()
    return render(request, 'wiki/history.html', {
        'game': game, 'page': page, 'revisions': revisions,
    })


def revision_detail(request, game_slug, slug, revision_number):
    game = get_object_or_404(Game, slug=game_slug)
    page = get_object_or_404(Page, game=game, slug=slug)
    revision = get_object_or_404(PageRevision, page=page, revision_number=revision_number)
    is_current = page.current_revision_id == revision.pk

    # Build a simple unified diff vs the previous revision
    diff_lines = []
    prev = page.revisions.filter(revision_number__lt=revision_number).first()
    if prev:
        diff_lines = list(difflib.unified_diff(
            prev.content.splitlines(keepends=True),
            revision.content.splitlines(keepends=True),
            fromfile=f'rev {prev.revision_number}',
            tofile=f'rev {revision.revision_number}',
            lineterm='',
        ))

    return render(request, 'wiki/revision_detail.html', {
        'game': game, 'page': page, 'revision': revision,
        'is_current': is_current, 'diff_lines': diff_lines,
    })


# ── Contributor views ─────────────────────────────────────────────────────────

@login_required
@contributor_required
def submit_edit(request, game_slug, slug):
    game = get_object_or_404(Game, slug=game_slug)
    page = get_object_or_404(Page, game=game, slug=slug, is_published=True)
    current_content = page.current_revision.content if page.current_revision else ''

    if request.method == 'POST':
        form = EditRequestForm(request.POST, initial_content=current_content)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.page = page
            edit.author = request.user
            edit.save()
            messages.success(request, 'Your edit has been submitted for moderation.')
            return redirect('wiki_detail', game_slug=game_slug, slug=slug)
    else:
        form = EditRequestForm(initial_content=current_content)

    return render(request, 'wiki/submit_edit.html', {
        'game': game, 'page': page, 'form': form,
    })


@login_required
@contributor_required
def create_page(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.game = game
            page.save()
            # Create the initial revision immediately
            revision = PageRevision.objects.create(
                page=page,
                author=request.user,
                content=form.cleaned_data['content'],
                edit_summary='Initial revision',
            )
            page.apply_revision(revision)
            messages.success(request, f'Page "{page.title}" created.')
            return redirect('wiki_detail', game_slug=game_slug, slug=page.slug)
    else:
        form = PageForm()
    return render(request, 'wiki/create_page.html', {'game': game, 'form': form})


# ── Moderator views ───────────────────────────────────────────────────────────

@login_required
@moderator_required
def moderation_queue(request):
    pending = EditRequest.objects.filter(
        status=EditRequest.STATUS_PENDING
    ).select_related('page', 'page__game', 'author').order_by('created_at')
    return render(request, 'wiki/moderation_queue.html', {'pending': pending})


@login_required
@moderator_required
def approve_edit(request, pk):
    edit = get_object_or_404(EditRequest, pk=pk)
    if request.method == 'POST':
        edit.approve(request.user)
        messages.success(request, f'Edit #{pk} approved and published.')
    return redirect('moderation_queue')


@login_required
@moderator_required
def reject_edit(request, pk):
    edit = get_object_or_404(EditRequest, pk=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        edit.reject(request.user, comment=comment)
        messages.warning(request, f'Edit #{pk} rejected.')
    return redirect('moderation_queue')


@login_required
@moderator_required
def restore_revision(request, game_slug, slug, revision_number):
    """Restore a previous revision as the current live version."""
    game = get_object_or_404(Game, slug=game_slug)
    page = get_object_or_404(Page, game=game, slug=slug)
    revision = get_object_or_404(PageRevision, page=page, revision_number=revision_number)
    if request.method == 'POST':
        page.apply_revision(revision)
        messages.success(request, f'Restored to revision #{revision_number}.')
        return redirect('wiki_detail', game_slug=game_slug, slug=slug)
    return render(request, 'wiki/confirm_restore.html', {
        'game': game, 'page': page, 'revision': revision,
    })

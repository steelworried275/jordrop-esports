from django.contrib import admin
from .models import EditRequest, Page, PageRevision


class PageRevisionInline(admin.TabularInline):
    model = PageRevision
    extra = 0
    readonly_fields = ['revision_number', 'author', 'edit_summary', 'created_at']
    fields = ['revision_number', 'author', 'edit_summary', 'created_at']
    can_delete = False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'game', 'is_published', 'updated_at']
    list_filter = ['game', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PageRevisionInline]
    readonly_fields = ['current_revision']


@admin.register(PageRevision)
class PageRevisionAdmin(admin.ModelAdmin):
    list_display = ['page', 'revision_number', 'author', 'edit_summary', 'created_at']
    list_filter = ['page__game']
    readonly_fields = ['revision_number', 'content_rendered']


@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):
    list_display = ['page', 'author', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'page__game']
    readonly_fields = ['author', 'page', 'proposed_content', 'edit_summary', 'created_at']

    def has_add_permission(self, request):
        return False

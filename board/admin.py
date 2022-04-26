from django.contrib import admin

# Register your models here.
from board.models import Board, Clipping, Comment, Revision, User, Wiki


class BoardAdmin(admin.ModelAdmin):
    list_display = ('board_id','user_id','wiki_id','board','board_title','board_content','board_num','board_place'
                    ,'board_recruitdate','board_time','board_on_off','board_phone','board_date',);
admin.site.register(Board,BoardAdmin);

class ClippingAdmin(admin.ModelAdmin):
    list_display =('clip_id','user_id','board_id');
admin.site.register(Clipping,ClippingAdmin);

class CommentAdmin(admin.ModelAdmin):
    list_display =('comment_id','board_id','user_id','comment_content','comment_date');
admin.site.register(Comment,CommentAdmin);

class RevisionAdmin(admin.ModelAdmin):
    list_display =('revi_id','revi_title','revi_content','revi_date','user_id');
admin.site.register(Revision,RevisionAdmin);

class UserAdmin(admin.ModelAdmin):
    list_display =('user_id','user_name','user_pwd','user_email','user_phone','favcom1','favcom2','favlang1','favlang2');
admin.site.register(User,UserAdmin);

class WikiAdmin(admin.ModelAdmin):
    list_display =('wiki_id','wiki_title','wiki_kind','wiki_content','revi_id');
admin.site.register(Wiki,WikiAdmin);
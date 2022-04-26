from django.db import models

# Create your models here.
class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    wiki = models.ForeignKey('Wiki', models.DO_NOTHING)
    board = models.CharField(max_length=10, blank=True, null=True)
    board_title = models.CharField(max_length=50, blank=True, null=True)
    board_content = models.TextField(blank=True, null=True)
    board_num = models.IntegerField(blank=True, null=True)
    board_place = models.CharField(max_length=20, blank=True, null=True)
    board_recruitdate = models.DateTimeField(blank=True, null=True)
    board_time = models.DateTimeField(blank=True, null=True)
    board_on_off = models.CharField(max_length=20, blank=True, null=True)
    board_phone = models.CharField(max_length=20, blank=True, null=True)
    board_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'board'


class Clipping(models.Model):
    clip_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    board = models.ForeignKey(Board, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'clipping'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    comment_content = models.TextField(blank=True, null=True)
    comment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'comment'

class Revision(models.Model):
    revi_id = models.AutoField(primary_key=True)
    revi_title = models.CharField(max_length=50, blank=True, null=True)
    revi_content = models.TextField(blank=True, null=True)
    revi_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'revision'


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20)
    user_name = models.CharField(max_length=10, blank=True, null=True)
    user_pwd = models.CharField(max_length=10, blank=True, null=True)
    user_email = models.CharField(max_length=20, blank=True, null=True)
    user_phone = models.CharField(max_length=20, blank=True, null=True)
    favcom1 = models.CharField(max_length=20, blank=True, null=True)
    favcom2 = models.CharField(max_length=20, blank=True, null=True)
    favlang1 = models.CharField(max_length=20, blank=True, null=True)
    favlang2 = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'


class Wiki(models.Model):
    wiki_id = models.AutoField(primary_key=True)
    wiki_title = models.CharField(max_length=50, blank=True, null=True)
    wiki_kind = models.CharField(max_length=20, blank=True, null=True)
    wiki_content = models.TextField(blank=True, null=True)
    revi = models.ForeignKey(Revision, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wiki'
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from django_request_mapping import request_mapping
from board.models import Board, User, Wiki, Revision, Comment
from django.utils import timezone

@request_mapping("")
class MyView(View):
    # 20220314 코드 추가 ####################################################
    @request_mapping("/clip/delete/", method="post")
    def scrap_delete(self, request):
        """
        스크랩 삭제 함수
        """
        from .models import Clipping
        from django.http import JsonResponse
        import json

        if 'sessionid' in request.session: # 로그인 체크

            try:
                data = json.loads(request.body)

                board = Board.objects.get(board_id=data)
                user = User.objects.get(user_id=request.session['sessionid'])
                clip = Clipping.objects.get(user_id=user,
                                            board_id=board)
                clip.delete()
                context = {
                    'result': data,
                }
            except:
                context = {
                    'result': 'fail',
                }
            return JsonResponse(context)
    #####################################################

    @request_mapping("/notice/scrap/", method="get")
    def notice_scrap(self, request):
        """
        스크랩 함수
        :param request:
        :return:
        """

        from .models import Clipping

        if 'sessionid' in request.session:
            type = request.GET['type']
            board = Board.objects.get(board_id=request.GET['board_id'])
            user = User.objects.get(user_id=request.session['sessionid'])
            try :
                cliped = Clipping.objects.get(user=user
                                              , board=board)  # 스크랩여부 체크
            except :
                cliped = None
            if not cliped :
                clip = Clipping(user = user,
                                board = board)
                clip.save()
                suc = 'Y'
            else :
                suc = 'dup'
            url = '/' + type + '/' + type
        else :
            url = '/login'
            suc = 'login'


        context = {'url' : url,
                   'suc' : suc}
        return render(request, 'clip/postok.html', context)

    @request_mapping("/scrap/scrap/", method="get")
    def scrap(self, request):
        """
        스크랩 리스트 화면
        """
        from django.shortcuts import redirect
        from .models import Clipping
        # 로그인 체크
        if 'sessionid' in request.session:
            user = User.objects.get(user_id=request.session['sessionid'])
            clips = Clipping.objects.filter(user_id=user) # 로그인한 유저가 등록한 board_id 가져오기
            boards = []
            if clips:
                for clip in clips :
                    boards.append(Board.objects.get(board_id = clip.board_id)) # board_id를 이용하여 Board정보 가져오기

            page = request.GET.get('page', '1')
            paginator = Paginator(boards, '10')
            page_obj = paginator.get_page(page)
            context = {'objs':page_obj}

            return render(request, 'clip/clip.html', context)
        else :
            return redirect('/login')

    @request_mapping("/clip/detail/<int:b_id>", method="get")
    def scrap_detail(self, request,b_id):
        from django.shortcuts import redirect
        commentpage = Comment.objects.filter(board_id=b_id)
        page = request.GET.get('page', '1');
        paginator = Paginator(commentpage, '10');
        page_obj = paginator.get_page(page);

        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id) # board_id로 Board정보 가져오기
            comments = Comment.objects.filter(board=board.board_id)

            context = {'board':board, 'comments':comments, 'center': 'comment.html', 'objs' : page_obj}

            return render(request, 'clip/detail.html', context)
        else :
            return redirect('/login')

    @request_mapping("/wiki/detail/", method="get")
    def wiki_detail(self, request):

        wiki = Wiki.objects.get(wiki_id=request.GET['wiki_id'])  # board_id로 Board정보 가져오기
        context = {'wiki': wiki}
        return render(request, 'wiki/detail_wiki.html', context)




    # ======================================================= 댓글 CRUD
    @request_mapping("/clip/comment/<int:b_id>", method="post")
    def comment_add(self, request, b_id):
        from django.shortcuts import redirect
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)  # board_id로 Board정보 가져오기
            user = User.objects.get(user_id=request.session['sessionid'])
            comment = Comment();
            comment.user = user
            comment.comment_date = timezone.now()
            comment.board = board
            comment.comment_content = request.POST['content']
            comment.save()

            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/clip/comment/uv/<int:b_id>/<int:c_id>/", method="get")
    def comment_updateView(self, request, b_id, c_id):
        from django.shortcuts import redirect
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)  # board_id로 Board정보 가져오기
            comments = Comment.objects.filter(board=board.board_id)
            comment = Comment.objects.get(comment_id=c_id);

            context = {'board': board,
                       'comment': comment,
                       'comments': comments}

            return render(request, 'clip/comment_update.html', context)
        else:
            return redirect('/login')

    @request_mapping("/clip/comment/u/<int:b_id>/<int:c_id>/", method="post")
    def comment_update(self, request, b_id, c_id):
        from django.shortcuts import redirect
        if 'sessionid' in request.session:
            comment = Comment.objects.get(comment_id=c_id);
            comment.comment_date = timezone.now()
            comment.comment_content = request.POST['content']
            comment.save()

            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/clip/comment/d/<int:b_id>/<int:c_id>/", method="get")
    def comment_delete(self, request, b_id, c_id):
        from django.shortcuts import redirect
        if 'sessionid' in request.session:
            comment = Comment.objects.get(comment_id=c_id);
            comment.delete();

            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/", method="get")
    def home(self,request):
        objs_notice = Board.objects.order_by('-board_date').filter(board='공지')[:5];
        objs_info = Board.objects.order_by('-board_date').filter(board='정보')[:5];
        objs_free = Board.objects.order_by('-board_date').filter(board='자유')[:5];
        objs_qna = Board.objects.order_by('-board_date').filter(board='질문')[:5];
        objs_study = Board.objects.order_by('-board_date').filter(board='스터디')[:5];
        objs_project = Board.objects.order_by('-board_date').filter(board='프로젝트')[:5];
        context = {
            'objs_notice':objs_notice,
            'objs_info': objs_info,
            'objs_free':objs_free,
            'objs_qna' : objs_qna,
            'objs_study':objs_study,
            'objs_project':objs_project
        }
        return render(request,'home.html',context);

    # 검색
    @request_mapping("/search", method="get")
    def search(self,request):
        context =[];
        search_type = request.GET['type']
        if request.GET['q'] =='':
            context={'message':'검색어는 2글자 이상 입력해주세요.'}
            return render(request,'search_board.html', context);
        search_word = request.GET['q']
        board_list = Board.objects.select_related('user');
        print(search_type, search_word)
        print(board_list.query)
        print('----------------')

        if search_word:
            if len(search_word) > 1 :
                if search_type == 'all':
                    search_board_list = board_list.filter(Q (board_title__icontains=search_word) | Q (board_content__icontains=search_word) | Q (user__user_id__icontains=search_word))
                elif search_type == 'title_content':
                    search_board_list = board_list.filter(Q (board_title__icontains=search_word) | Q (board_content__icontains=search_word))
                elif search_type == 'title':
                    search_board_list = board_list.filter(board_title__icontains=search_word)
                elif search_type == 'content':
                    search_board_list = board_list.filter(board_content__icontains=search_word)
                elif search_type == 'writer':
                    search_board_list = board_list.filter(user__user_id__icontains=search_word)
                context={
                    'search_boards':search_board_list,
                    'search_term':search_word
                }
            else:
                context={'message':'검색어는 2글자 이상 입력해주세요.'}
                # messages.error(self.request, '검색어는 2글자 이상 입력해주세요.')
        return render(request,'search_board.html', context);

    @request_mapping("/wiki/search", method="get")
    def wikisearch(self, request):
        context = [];
        if request.GET['q'] == '':
            context = {'message': '검색어는 2글자 이상 입력해주세요.'}
            return render(request, 'search_wiki.html', context);

        search_word = request.GET['q']
        wiki_list = Wiki.objects.select_related('revi');


        if search_word:
            if len(search_word) > 1:
                search_wiki_list =wiki_list.filter(wiki_title__icontains=search_word)

                context = {
                    'search_wikis': search_wiki_list,
                    'search_term': search_word
                }
            else:
                context = {'message': '검색어는 2글자 이상 입력해주세요.'}
                # messages.error(self.request, '검색어는 2글자 이상 입력해주세요.')
        return render(request, 'search_wiki.html', context);


    # ================================================================
    @request_mapping("/notice/notice", method="get") #공지사항
    def notice(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='공지');
        page = request.GET.get('page','1');
        paginator = Paginator(objs,'10');
        page_obj = paginator.get_page(page);
        context = {
            'objs': page_obj
        };
        return render(request, 'notice/notice.html', context);

    @request_mapping("/notice/post", method="get")  # 공지사항
    def noticepost(self, request):
        if 'admin' != request.session['sessionid']:
            return render(request, 'notice/noadmin.html');
        return render(request, 'notice/post.html');

    @request_mapping("/notice/notice/p", method="post")  # 공지사항
    def notice_post(self, request):
        title = request.POST['title'];
        text = request.POST['content'];
        try:
                data = Board(board_title=title, board='공지', user_id=request.session['sessionid'], wiki_id='1', board_content=text,
                             board_date=timezone.now());
                data.save()
                return render(request, 'notice/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 공지 UD
    @request_mapping("/notice/uv/<int:b_id>/", method="get")
    def notice_updateView(self, request, b_id):
        if 'admin' != request.session['sessionid']:
            return render(request, 'notice/noadmin.html');
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)

            context = {
                'board': board
            }
            return render(request, 'notice/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/notice/u/<int:b_id>/", method="post")
    def notice_update(self, request, b_id):
        if 'admin' != request.session['sessionid']:
            return render(request, 'notice/noadmin.html');
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['title']
            board.board_content = request.POST['content']


            board.save()

            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/notice/d/<int:b_id>/", method="get")
    def notice_delete(self, request, b_id):
        if 'admin' != request.session['sessionid']:
            return render(request, 'notice/noadmin.html');
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()

            return redirect('/notice/notice')
        else:
            return redirect('/login')

    # ================================================================

    @request_mapping("/info/info", method="get") #정보게시판
    def info(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='정보');
        page = request.GET.get('page', '1');
        paginator = Paginator(objs, '10');
        page_obj = paginator.get_page(page);
        context = {
            'objs': page_obj
        };
        return render(request, 'info/info.html', context);

    @request_mapping("/info/post", method="get")  # 공지사항
    def infopost(self, request):
        wiki = Wiki.objects.all()
        objs = [];
        for i in range(0, len(wiki)):
            objs.append(wiki[i].wiki_title)
        context = {
            'objs': objs
        }
        return render(request, 'info/post.html', context);

    @request_mapping("/info/info/p", method="post")  # 공지사항
    def info_post(self, request):
        wiki_title = request.POST['wiki'];
        if wiki_title == '공지':
            return render(request, 'error/wikipostfail.html');
        try:
            wiki = Wiki.objects.get(wiki_title = wiki_title)
        except:
            return render(request, 'error/wikiexistfail.html');
        title = request.POST['title'];
        text = request.POST['content'];
        try:
                data = Board(board_title=title, board='정보', user_id=request.session['sessionid'], wiki_id=wiki.wiki_id,
                             board_content=text,
                             board_date= timezone.now());
                data.save()
                return render(request, 'info/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 정보 UD
    @request_mapping("/info/uv/<int:b_id>/", method="get")
    def info_updateView(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            wiki = Wiki.objects.all()
            objs = [];
            for i in range(0, len(wiki)):
                objs.append(wiki[i].wiki_title)

            context = {
                'board': board,
                'objs': objs,
            }
            return render(request, 'info/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/info/u/<int:b_id>/", method="post")
    def info_update(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['title']
            board.board_content = request.POST['content']

            try:
                if request.POST['wiki'] == '공지':
                    return render(request, 'error/wikipostfail.html');
                wiki_board = Wiki.objects.get(wiki_title=request.POST['wiki'])

                board.wiki_id = wiki_board.wiki_id
                board.save()
            except:
                return render(request, 'error/wikiexistfail.html');



            # wiki = Wiki.objects.get(wiki_title=board.wiki_title)


            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/info/d/<int:b_id>/", method="get")
    def info_delete(self, request, b_id):
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()


            return redirect('/info/info')
        else:
            return redirect('/login')

    # ================================================================
    @request_mapping("/free/free", method="get") #자유게시판
    def free(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='자유');
        page = request.GET.get('page', '1');
        paginator = Paginator(objs, '10');
        page_obj = paginator.get_page(page);

        context = {
            'objs': page_obj
        };
        return render(request, 'free/free.html',context);

    @request_mapping("/free/post", method="get")  # 공지사항
    def freepost(self, request):
        wiki = Wiki.objects.all()
        objs = [];
        for i in range(0,len(wiki)):
            objs.append(wiki[i].wiki_title)
        context = {
            'objs':objs
        }
        return render(request, 'free/post.html', context);

    @request_mapping("/free/free/p", method="post")  # 공지사항
    def free_insert(self, request):
        title = request.POST['title'];
        text = request.POST['content'];

        wiki_title = request.POST['wiki'];
        if wiki_title == '공지':
            return render(request, 'error/wikipostfail.html');
        try:
            wiki = Wiki.objects.get(wiki_title = wiki_title)
        except:
            return render(request, 'error/wikiexistfail.html');

        try:
                data = Board(board_title=title, board='자유', user_id=request.session['sessionid'], wiki_id=wiki.wiki_id,
                             board_content=text,
                             board_date=timezone.now());
                data.save()
                return render(request, 'free/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 2022-03-16 코드 추가
    # 자유 UD
    @request_mapping("/free/uv/<int:b_id>/", method="get")
    def free_updateView(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            wiki = Wiki.objects.all()
            objs = [];
            for i in range(0, len(wiki)):
                objs.append(wiki[i].wiki_title)

            context = {
                'board': board,
                'objs': objs,
            }
            return render(request, 'free/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/free/u/<int:b_id>/", method="post")
    def free_update(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['title']
            board.board_content = request.POST['content']

            try:
                if request.POST['wiki'] == '공지':
                    return render(request, 'error/wikipostfail.html');
                wiki_board = Wiki.objects.get(wiki_title=request.POST['wiki'])

                board.wiki_id = wiki_board.wiki_id
                board.save()
            except:
                return render(request, 'error/wikiexistfail.html');
            # wiki = Wiki.objects.get(wiki_title=board.wiki_title)


            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/free/d/<int:b_id>/", method="get")
    def free_delete(self, request, b_id):
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()

            return redirect('/free/free')
        else:
            return redirect('/login')

    # ================================================================
    @request_mapping("/qna/qna", method="get") #질문게시판
    def qna(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='질문');

        page = request.GET.get('page', '1');
        paginator = Paginator(objs, '10');
        page_obj = paginator.get_page(page);
        context = {
            'objs': page_obj
        };
        return render(request, 'qna/qna.html',context);

    @request_mapping("/qna/post", method="get")  # 공지사항
    def qnapost(self, request):
        wiki = Wiki.objects.all()
        objs = [];
        for i in range(0, len(wiki)):
            objs.append(wiki[i].wiki_title)
        context = {
            'objs': objs
        }
        return render(request, 'qna/post.html', context);

    @request_mapping("/qna/qna/p", method="post")  # 질문
    def qna_insert(self, request):
        title = request.POST['title'];
        text = request.POST['content'];
        wiki_title = request.POST['wiki'];
        if wiki_title == '공지':
            return render(request, 'error/wikipostfail.html');
        try:
            wiki = Wiki.objects.get(wiki_title=wiki_title)
        except:
            return render(request, 'error/wikiexistfail.html');
        try:
            data = Board(board_title=title, board='질문', user_id=request.session['sessionid'], wiki_id=wiki.wiki_id,
                         board_content=text,
                         board_date=timezone.now());
            data.save()
            return render(request, 'qna/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 질문 UD
    @request_mapping("/qna/uv/<int:b_id>/", method="get")
    def qna_updateView(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            wiki = Wiki.objects.all()
            objs = [];
            for i in range(0, len(wiki)):
                objs.append(wiki[i].wiki_title)

            context = {
                'board': board,
                'objs': objs,
            }
            return render(request, 'qna/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/qna/u/<int:b_id>/", method="post")
    def qna_update(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['title']
            board.board_content = request.POST['content']
            try:
                if request.POST['wiki'] == '공지':
                    return render(request, 'error/wikipostfail.html');
                wiki_board = Wiki.objects.get(wiki_title=request.POST['wiki'])

                board.wiki_id = wiki_board.wiki_id
                board.save()
            except:
                return render(request, 'error/wikiexistfail.html');
            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/qna/d/<int:b_id>/", method="get")
    def qna_delete(self, request, b_id):
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()

            return redirect('/qna/qna')
        else:
            return redirect('/login')

    # ================================================================
    @request_mapping("/project/project", method="get") #프로젝트
    def project(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='프로젝트');

        page = request.GET.get('page', '1');
        paginator = Paginator(objs, '10');
        page_obj = paginator.get_page(page);
        context = {
            'objs': page_obj
        };
        return render(request, 'project/project.html', context);

    @request_mapping("/project/post", method="get")  #
    def projectpost(self, request):
        wiki = Wiki.objects.all()
        objs = [];
        for i in range(0, len(wiki)):
            objs.append(wiki[i].wiki_title)
        context = {
            'objs': objs
        }
        return render(request, 'project/post.html', context);

    @request_mapping("/project/project/p", method="post")  # 질문
    def project_insert(self, request):
        title = request.POST['board_title'];
        content = request.POST['board_content'];
        num = request.POST['board_num'];
        place = request.POST['board_place'];
        recruitdate = request.POST['board_recruitdate'];
        time = request.POST['board_time'];
        on_off = request.POST['board_on_off'];
        phone = request.POST['board_phone'];
        wiki_title = request.POST['wiki'];
        if wiki_title == '공지':
            return render(request, 'error/wikipostfail.html');
        try:
            wiki = Wiki.objects.get(wiki_title=wiki_title)
        except:
            return render(request, 'error/wikiexistfail.html');
        try:
            data = Board(board_title=title, board='프로젝트', user_id=request.session['sessionid'], wiki_id=wiki.wiki_id,
                         board_content=content,
                         board_date=timezone.now(),board_num = num, board_place = place,
                         board_recruitdate = recruitdate, board_time = time, board_on_off = on_off,
                         board_phone = phone);
            data.save()
            return render(request, 'project/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 프로젝트 UD
    @request_mapping("/project/uv/<int:b_id>/", method="get")
    def project_updateView(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            wiki = Wiki.objects.all()
            objs = [];
            for i in range(0, len(wiki)):
                objs.append(wiki[i].wiki_title)

            context = {
                'board': board,
                'objs': objs,
            }
            return render(request, 'project/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/project/u/<int:b_id>/", method="post")
    def project_update(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['board_title']
            board.board_content = request.POST['board_content']
            board.board_num = request.POST['board_num']
            board.board_place = request.POST['board_place']
            board.board_phone = request.POST['board_phone']
            board.board_on_off = request.POST['board_on_off']
            board.board_recruitdate = request.POST['board_recruitdate']
            board.board_time = request.POST['board_time']
            try:
                if request.POST['wiki'] == '공지':
                    return render(request, 'error/wikipostfail.html');
                wiki_board = Wiki.objects.get(wiki_title=request.POST['wiki'])

                board.wiki_id = wiki_board.wiki_id
                board.save()
            except:
                return render(request, 'error/wikiexistfail.html');
            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/project/d/<int:b_id>/", method="get")
    def project_delete(self, request, b_id):
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()

            return redirect('/project/project')
        else:
            return redirect('/login')


    # ================================================================
    @request_mapping("/study/study", method="get") #스터디
    def study(self, request):
        objs = Board.objects.order_by('-board_date').filter(board='스터디');

        page = request.GET.get('page', '1');
        paginator = Paginator(objs, '10');
        page_obj = paginator.get_page(page);
        context = {
            'objs': page_obj
        };
        return render(request, 'study/study.html',context);

    @request_mapping("/study/post", method="get")  # 스터디로
    def studypost(self, request):
        wiki = Wiki.objects.all()
        objs = [];
        for i in range(0, len(wiki)):
            objs.append(wiki[i].wiki_title)
        context = {
            'objs': objs
        }
        return render(request, 'study/post.html', context);

    @request_mapping("/study/study/p", method="post")  # 질문
    def study_insert(self, request):
        title = request.POST['board_title'];
        content = request.POST['board_content'];
        num = request.POST['board_num'];
        place = request.POST['board_place'];
        recruitdate = request.POST['board_recruitdate'];
        time = request.POST['board_time'];
        on_off = request.POST['board_on_off'];
        phone = request.POST['board_phone'];
        wiki_title = request.POST['wiki'];
        if wiki_title == '공지':
            return render(request, 'error/wikipostfail.html');
        try:
            wiki = Wiki.objects.get(wiki_title=wiki_title)
        except:
            return render(request, 'error/wikiexistfail.html');
        try:
            data = Board(board_title=title, board='스터디', user_id=request.session['sessionid'], wiki_id=wiki.wiki_id,
                         board_content=content,
                         board_date=timezone.now(),board_num = num, board_place = place,
                         board_recruitdate = recruitdate, board_time = time, board_on_off = on_off,
                         board_phone = phone);
            data.save()
            return render(request, 'study/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    # 스터디 UD
    @request_mapping("/study/uv/<int:b_id>/", method="get")
    def study_updateView(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            wiki = Wiki.objects.all()
            objs = [];
            for i in range(0, len(wiki)):
                objs.append(wiki[i].wiki_title)

            context = {
                'board': board,
                'objs': objs,
            }
            return render(request, 'study/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/study/u/<int:b_id>/", method="post")
    def study_update(self, request, b_id):
        if 'sessionid' in request.session:
            board = Board.objects.get(board_id=b_id)
            board.board_title = request.POST['board_title']
            board.board_content = request.POST['board_content']
            board.board_num = request.POST['board_num']
            board.board_place = request.POST['board_place']
            board.board_phone = request.POST['board_phone']
            board.board_on_off = request.POST['board_on_off']
            board.board_recruitdate = request.POST['board_recruitdate']
            board.board_time = request.POST['board_time']
            try:
                if request.POST['wiki'] == '공지':
                    return render(request, 'error/wikipostfail.html');
                wiki_board = Wiki.objects.get(wiki_title=request.POST['wiki'])

                board.wiki_id = wiki_board.wiki_id
                board.save()
            except:
                return render(request, 'error/wikiexistfail.html');

            return redirect('/clip/detail/{}'.format(b_id))
        else:
            return redirect('/login')

    @request_mapping("/study/d/<int:b_id>/", method="get")
    def study_delete(self, request, b_id):
        if 'sessionid' in request.session:
            comment = Comment.objects.filter(board_id=b_id)
            comment.delete()
            board = Board.objects.get(board_id=b_id)
            board.delete()

            return redirect('/study/study')
        else:
            return redirect('/login')

    # ================================================================
    @request_mapping("/post", method="get")
    def post(self, request):
        return render(request, 'post.html');

    # ================================================================
    @request_mapping("/wiki/wiki", method="get")
    def wiki(self, request):
        return render(request, 'wiki/wiki.html');

    @request_mapping("/wiki/post", method="get")  # 공지사항
    def wikipost(self, request):
        return render(request, 'wiki/post.html');

    @request_mapping("/wiki/wiki/p", method="post")  # 질문
    def wiki_insert(self, request):
        title = request.POST['wiki_title'];
        text = request.POST['content'];
        revitext = request.POST['revi_content'];
        kind = request.POST['kind']
        userid = User.objects.get(user_id = request.session['sessionid'])
        try:
            wikiall = Wiki.objects.all();
            for i in wikiall:
                if i.wiki_title == title: #제목이 이미 있으면
                    print(i.wiki_title)
                    raise Exception; #에러발생

        except:
            return render(request, 'wiki/postfail.html');

        try:
            data2 = Revision(revi_title = title, revi_content = revitext, user_id = userid.user_id)
            data2.save()
            revi1 = Revision.objects.get(revi_title = title)
            data = Wiki(wiki_title=title, wiki_kind=kind, wiki_content=text,revi_id = revi1.revi_id);
            data.save()
            return render(request, 'wiki/postok.html');
        except:  # id 값이 없으므로 에러가 남
            return render(request, 'postfail.html');

    @request_mapping("/wiki/uv/<int:w_id>/", method="get")
    def wiki_updateView(self, request, w_id):
        if 'sessionid' in request.session:
            wiki = Wiki.objects.get(wiki_id=w_id)
            # wikis = Wiki.objects.all()
            # objs = [];
            # for i in range(0, len(wiki)):
            #     objs.append(wiki[i].wiki_title)

            context = {
                'wiki': wiki,
                # 'objs': objs,
            }
            return render(request, 'wiki/update.html', context)
        else:
            return redirect('/home')

    @request_mapping("/wiki/u/<int:w_id>/", method="post")
    def wiki_update(self, request, w_id):
        if 'sessionid' in request.session:
            wiki = Wiki.objects.get(wiki_id=w_id)
            wiki.wiki_content = request.POST['content']
            revi_user = Revision.objects.get(revi_id = wiki.revi_id)
            revi_user.user_id = request.session['sessionid']
            revi_user.revi_content = request.POST['revi_content']
            revi_user.revi_title = request.POST['revi_title']
            revi_user.save()
            wiki.save()

            return redirect('/wiki/detail/?wiki_id={}'.format(w_id))
        else:
            return redirect('/login')

    # ================================================================
    @request_mapping("/register", method="get")  # 회원가입
    def register(self, request):
        return render(request, 'register.html');

    @request_mapping("/registerimpl", method="post")
    def registerimpl(self, request):
        user_id = request.POST['user_id'];
        user_pwd = request.POST['user_pwd'];
        user_name = request.POST['user_name'];
        user_email = request.POST['user_email'];
        user_phone = request.POST['user_phone'];
        favcom1 = request.POST['favcom1'];
        favcom2 = request.POST['favcom2'];
        favlang1 = request.POST['favlang1'];
        favlang2 = request.POST['favlang2'];

        context = {}
        try:
            User.objects.get(user_id=user_id)
            context['center'] = 'registerfail.html'
        except:
            User(user_id=user_id, user_pwd=user_pwd, user_name=user_name, user_email=user_email,
                 user_phone=user_phone, favcom1=favcom1, favcom2=favcom2, favlang1=favlang1, favlang2=favlang2).save()
            context['center'] = 'registerok.html'

        return render(request, 'home.html', context)

    @request_mapping("/login", method="get")  # 공지사항
    def login(self, request):
        return render(request, 'login.html');

    @request_mapping("/loginimpl", method="post")  # 공지사항
    def loginimpl(self, request):

        user_id = request.POST['id']
        user_pwd = request.POST['pwd']

        try:
            user = User.objects.get(user_id=user_id)
            if user.user_pwd == user_pwd:
                request.session['sessionid'] = user.user_id;
                request.session['sessionname'] = user.user_name;
                objs_notice = Board.objects.order_by('-board_date').filter(board='공지')[:5];
                objs_info = Board.objects.order_by('-board_date').filter(board='정보')[:5];
                objs_free = Board.objects.order_by('-board_date').filter(board='자유')[:5];
                objs_qna = Board.objects.order_by('-board_date').filter(board='질문')[:5];
                objs_study = Board.objects.order_by('-board_date').filter(board='스터디')[:5];
                objs_project = Board.objects.order_by('-board_date').filter(board='프로젝트')[:5];
                context = {
                    'objs_notice': objs_notice,
                    'objs_info': objs_info,
                    'objs_free': objs_free,
                    'objs_qna': objs_qna,
                    'objs_study': objs_study,
                    'objs_project': objs_project
                }
                return render(request, 'home.html',context);
            else:
                raise Exception
        except:
            return render(request, 'loginfail.html');

    @request_mapping("/logout", method="get")
    def logout(self, request):
        if request.session['sessionid'] != None:
            del request.session['sessionid']
        objs_notice = Board.objects.order_by('-board_date').filter(board='공지')[:5];
        objs_info = Board.objects.order_by('-board_date').filter(board='정보')[:5];
        objs_free = Board.objects.order_by('-board_date').filter(board='자유')[:5];
        objs_qna = Board.objects.order_by('-board_date').filter(board='질문')[:5];
        objs_study = Board.objects.order_by('-board_date').filter(board='스터디')[:5];
        objs_project = Board.objects.order_by('-board_date').filter(board='프로젝트')[:5];
        context = {
            'objs_notice': objs_notice,
            'objs_info': objs_info,
            'objs_free': objs_free,
            'objs_qna': objs_qna,
            'objs_study': objs_study,
            'objs_project': objs_project
        }
        return render(request, 'home.html',context)

    @request_mapping("/mypage", method="get")
    def mypage(self, request):
        user_id = request.session['sessionid']

        user = User.objects.get(user_id=user_id)
        context = {
            'user': user
        }
        return render(request, 'mypage.html', context)
from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo, Comment
from datetime import datetime
from djangodb.AccountDao import AccountDao
from djangodb.WeiboDao import WeiboDao

class CommentDao:

    @staticmethod
    def create_or_update(commentJson):
        comment = commentJson
        cmt, created = Comment.objects.get_or_create(c_id=comment[u'id'])

        if created:
            if comment[u'created_at']:
                cmt.created_at = datetime.strptime(comment[u'created_at'], "%a %b %d %H:%M:%S +0800 %Y")
            cmt.text = comment[u'text']
            if u'source' in comment:
                cmt.source = comment[u'source']
            cmt.owner = AccountDao.create_or_update(comment[u'user'])
            if u'status' in comment:
                cmt.commented_status = WeiboDao.create_or_update(comment[u'status'])
            cmt.fetched_at = datetime.now()
            if u'reply_comment' in comment:
                cmt.reply_comment = CommentDao.create_or_update(comment[u'reply_comment'])
            cmt.save()
      
        return cmt


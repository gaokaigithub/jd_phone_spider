from peewee import *

db = MySQLDatabase('python_spider', user='root', password='123456', host="localhost", port=3306, charset='utf8')


class BaseModel(Model):
    class Meta:
        database = db


class Brand(BaseModel):
    '''商品所属品牌'''
    id = CharField(primary_key=True, verbose_name="品牌id")
    name = CharField(default="", verbose_name="品牌")
    phone_nums = IntegerField(default=0, verbose_name="手机数量")


class Good(BaseModel):
    '''商品详情（简单版）'''
    id = BigIntegerField(primary_key=True, verbose_name="商品id")
    name = CharField(max_length=500, verbose_name="商品标题")
    brand = ForeignKeyField(Brand, verbose_name='品牌')
    price = FloatField(default=0.0, verbose_name="价格")
    colors = TextField(default="", verbose_name="可选颜色")
    memories = CharField(default="", verbose_name="可选版本")
    comment_percent = IntegerField(default=100, verbose_name="好评度(%)")
    comment_nums = IntegerField(default=0, verbose_name="评论数")
    image_comment_nums = IntegerField(default=0, verbose_name="晒图数")
    video_comment_nums = IntegerField(default=0, verbose_name="视频晒单数")
    added_comment_nums = IntegerField(default=0, verbose_name="追评数")
    positive_comment_nums = IntegerField(default=0, verbose_name="好评数")
    middle_comment_nums = IntegerField(default=0, verbose_name="中评数")
    negative_comment_nums = IntegerField(default=0, verbose_name="差评数")


class GoodReviewsTag(BaseModel):
    '''商品的评价标签和标签点击数量'''
    id = CharField(primary_key=True, verbose_name="标签id")
    good = ForeignKeyField(Good, verbose_name="商品")
    tag = CharField(default="", max_length=20, verbose_name="评价标签")
    tag_num = IntegerField(default=0, verbose_name="数量")

# if __name__ == "__main__":
#     db.connect()
#     if not db.table_exists(['brand','good','goodreviewstag']):
#         # Brand, Good,
#         db.create_tables([Brand, Good, GoodReviewsTag])

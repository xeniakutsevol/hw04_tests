import shutil
import tempfile

from ..forms import PostForm
from ..models import Post, Group
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import datetime as dt

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
            pk=100,
            group=cls.group,
            pub_date=dt.datetime(2022, 3, 3)
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(User.objects.get(username='auth'))

    def test_create_post(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()

        form_data = {
            'author': PostFormTests.post.author,
            'text': PostFormTests.post.text,
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.post.group.id,
            'pub_date': PostFormTests.post.pub_date
        }

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response,
                             reverse('posts:profile', kwargs={'username':
                                     f'{PostFormTests.post.author.username}'}))
        self.assertRedirects(response_guest,
                             '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.post.author,
                text=PostFormTests.post.text,
                pk=PostFormTests.post.pk,
                group=PostFormTests.post.group,
                pub_date=PostFormTests.post.pub_date
            ).exists()
        )

    def test_post_edit(self):
        posts_count = Post.objects.count()

        form_data = {
            'author': PostFormTests.post.author,
            'text': 'Новый текст',
            'pk': PostFormTests.post.pk,
            'group': PostFormTests.group.id,
            'pub_date': PostFormTests.post.pub_date
        }

        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostFormTests.post.pk}'}),
            data=form_data,
            follow=True
        )
        response_guest = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostFormTests.post.pk}'}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': f'{PostFormTests.post.pk}'}))
        self.assertRedirects(response_guest, f'/auth/login/?next=/posts/'
                             f'{PostFormTests.post.pk}/edit/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.post.author,
                text='Новый текст',
                pk=PostFormTests.post.pk,
                group=PostFormTests.group,
                pub_date=PostFormTests.post.pub_date
            ).exists()
        )

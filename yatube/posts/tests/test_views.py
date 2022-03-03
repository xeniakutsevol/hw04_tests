from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post
from django.urls import reverse
# import datetime as dt
from django import forms

User = get_user_model()

POSTS_PER_PAGE = 10


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.additional_user = User.objects.create_user(username='add_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.additional_group = Group.objects.create(
            title='Еще одна группа',
            slug='new_group',
            description='Тестовое описание новой группы',
        )
        for i in range(1, 6):
            Post.objects.create(
                author=cls.additional_user,
                text=f'Тестовый пост номер {i}',
                pk=i,
                group=cls.additional_group,
                # pub_date=dt.datetime(2022, 2, 27)
            )
        for i in range(6, 11):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост номер {i}',
                pk=i,
                # pub_date=dt.datetime(2022, 2, 28)
            )

        for i in range(11, 26):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост номер {i}',
                pk=i,
                group=cls.group,
                # pub_date=dt.datetime(2022, 3, 1)
            )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
            pk=100,
            group=cls.group,
            # pub_date=dt.datetime(2022, 3, 3)
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(User.objects.get(username='auth'))

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug':
                    f'{PostViewTests.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    f'{PostViewTests.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{PostViewTests.post.pk}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostViewTests.post.pk}'}): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_correct_context(self):
        """Тестирование контекста и паджинатора страниц."""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug':
                    f'{PostViewTests.group.slug}'}),
            reverse('posts:profile', kwargs={'username':
                    f'{PostViewTests.user.username}'})
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_PAGE)
                last_post = Post.objects.order_by('-pub_date').first()
                first_object = response.context['page_obj'][0]
                post_author_0 = first_object.author.username
                post_text_0 = first_object.text
                post_pk_0 = first_object.pk
                post_group_0 = first_object.group.title
                self.assertEqual(post_author_0, last_post.author.username)
                self.assertEqual(post_text_0, last_post.text)
                self.assertEqual(post_pk_0, last_post.pk)
                self.assertEqual(post_group_0, last_post.group.title)

    def test_post_detail_correct_context(self):
        """Тестирование контекста страницы поста."""
        response = (self.guest_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': f'{PostViewTests.post.pk}'})))
        self.assertEqual(response.context.get('post').text,
                         f'{PostViewTests.post.text}')
        self.assertEqual(response.context.get('post').author.username,
                         f'{PostViewTests.post.author.username}')
        self.assertEqual(response.context.get('post').group.title,
                         f'{PostViewTests.post.group}')
        self.assertEqual(response.context.get('post').pk,
                         PostViewTests.post.pk)
        self.assertEqual((
            response.context.get('post').pub_date).strftime("%Y:%m:%d"),
            (PostViewTests.post.pub_date).strftime("%Y:%m:%d"))
        author_posts_count = Post.objects.filter(
            author=PostViewTests.post.author).count()
        self.assertEqual(response.context.get('author_posts_count'),
                         author_posts_count)

    def test_post_create_edit_correct_context(self):
        """Тестирование контекста страницы создания и редактирования поста."""

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        reverse_names = (
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostViewTests.post.pk}'}),
            reverse('posts:post_create'),
        )

        for reverse_name in reverse_names:
            response = self.author_client.get(reverse_name)

            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_with_group_in_right_pages(self):
        """Посты с группой попадают на верные страницы."""
        reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug':
                    f'{PostViewTests.group.slug}'}),
            reverse('posts:profile', kwargs={'username':
                    f'{PostViewTests.user.username}'}),
        )

        for reverse_name in reverse_names:
            response = self.authorized_client.get(reverse_name)
            self.assertIn(PostViewTests.post, response.context['page_obj'])
        wrong_group = reverse('posts:group_list', kwargs={'slug':
                              f'{PostViewTests.additional_group.slug}'})
        response = self.authorized_client.get(wrong_group)
        self.assertNotIn(PostViewTests.post, response.context['page_obj'])

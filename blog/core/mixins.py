from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class OnlyProfileOwnerMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.get_object()
        return user == self.request.user

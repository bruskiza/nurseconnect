from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from nurseconnect.constants import GENDERS
from molo.commenting.models import MoloComment
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class NurseConnectUserProfile(models.Model):
    user = models.OneToOneField(
        User,
        related_name="nurse_connect_profile",
        primary_key=True
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDERS,
        blank=True,
        null=True
    )
    mobile_number = models.CharField(
        max_length=15
    )
    staff_number = models.CharField(
        max_length=15
    )
    facility_code = models.CharField(
        max_length=15
    )
    security_question_1_answer = models.CharField(
        max_length=128,
        null=True
    )
    security_question_2_answer = models.CharField(
        max_length=128,
        null=True
    )

    # based on django.contrib.auth.models.AbstractBaseUser set_password &
    # check_password functions (takes plain text, generates hash for database)
    def set_security_question_1_answer(self, raw_answer):
        self.security_question_1_answer = make_password(
            raw_answer.strip().lower()
        )

    def set_security_question_2_answer(self, raw_answer):
        self.security_question_2_answer = make_password(
            raw_answer.strip().lower()
        )

    def check_security_question_1_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_security_question_1_answer(raw_answer)
            self.save(update_fields=["security_question_1_answer"])

        return check_password(
            raw_answer.strip().lower(), self.security_question_1_answer, setter
        )

    def check_security_question_2_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_security_question_2_answer(raw_answer)
            self.save(update_fields=["security_question_2_answer"])

        return check_password(
            raw_answer.strip().lower(), self.security_question_2_answer, setter
        )


@receiver(post_save, sender=User)
def nurse_connect_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = NurseConnectUserProfile(user=instance)
        profile.save()


@register_setting
class NurseConnectSettings(BaseSetting):
    banned_keywords_and_patterns = models.TextField(
        verbose_name="Banned Keywords and Patterns",
        null=True,
        blank=True,
        help_text="Banned keywords and patterns for comments, separated by a"
                  " line a break. Use only lowercase letters for keywords."
    )
    panels = [
        FieldPanel("banned_keywords_and_patterns")
    ]


class NurseConnectCommentReport(models.Model):
    user = models.ForeignKey(User)
    comment = models.ForeignKey(MoloComment)
    reported_reason = models.CharField(
        max_length=128,
        blank=False
    )

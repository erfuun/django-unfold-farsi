import datetime

import jdatetime
from django import forms
from django.db import models
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase
from django.utils import timezone

from unfold_farsi.admin import (
    JalaliAdminDateWidget,
    JalaliAdminSplitDateTimeWidget,
    JalaliAdminTimeWidget,
    JalaliDateListFilter,
    JalaliInlineMixin,
    JalaliModelAdminMixin,
    ModelAdmin,
    StackedInline,
    TabularInline,
)
from unfold_farsi.jalali import (
    format_jalali,
    jalali_relative_time,
    parse_jalali,
    to_ascii_digits,
    to_gregorian,
    to_jalali,
    to_persian_digits,
)
from unfold_farsi.widgets import (
    JalaliDateField,
    JalaliDateTimeField,
    JalaliDateWidget,
    JalaliSplitDateTimeWidget,
    JalaliTimeField,
    JalaliTimeWidget,
)


class DummyModel(models.Model):
    name = models.CharField(max_length=100)
    event_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = "formula"
        verbose_name = "Dummy Model"

    def __str__(self):
        return self.name


class JalaliCoreTests(SimpleTestCase):
    def test_digit_conversions(self):
        self.assertEqual(to_persian_digits("1234567890"), "۱۲۳۴۵۶۷۸۹۰")
        self.assertEqual(to_persian_digits(1403), "۱۴۰۳")
        self.assertEqual(to_persian_digits(None), "")

        self.assertEqual(to_ascii_digits("۱۲۳۴۵۶۷۸۹۰"), "1234567890")
        self.assertEqual(to_ascii_digits("١٢٣٤٥٦٧٨٩٠"), "1234567890")
        self.assertEqual(to_ascii_digits(None), "")

    def test_to_jalali_date_and_datetime(self):
        g_date = datetime.date(2024, 9, 15)
        j_date = to_jalali(g_date)
        self.assertIsInstance(j_date, jdatetime.date)
        self.assertEqual(j_date.year, 1403)
        self.assertEqual(j_date.month, 6)
        self.assertEqual(j_date.day, 25)

        g_dt = datetime.datetime(2024, 9, 15, 14, 30, tzinfo=datetime.timezone.utc)
        j_dt = to_jalali(g_dt)
        self.assertIsInstance(j_dt, jdatetime.datetime)

        # ISO strings
        self.assertEqual(to_jalali("2024-09-15").year, 1403)
        self.assertIsNone(to_jalali(None))
        self.assertIsNone(to_jalali(""))
        self.assertIsNone(to_jalali("invalid-date"))

    def test_to_gregorian(self):
        j_date = jdatetime.date(1403, 6, 25)
        g_date = to_gregorian(j_date)
        self.assertEqual(g_date, datetime.date(2024, 9, 15))

        j_dt = jdatetime.datetime(1403, 6, 25, 12, 0)
        g_dt = to_gregorian(j_dt)
        self.assertEqual(g_dt, datetime.datetime(2024, 9, 15, 12, 0))

    def test_format_jalali(self):
        g_date = datetime.date(2024, 9, 15)
        # Persian numerals by default
        self.assertEqual(format_jalali(g_date, "Y/m/d"), "۱۴۰۳/۰۶/۲۵")
        # Latin numerals flag
        self.assertEqual(format_jalali(g_date, "Y/m/d", latin=True), "1403/06/25")
        # Persian month name
        self.assertEqual(format_jalali(g_date, "j F Y", latin=True), "25 شهریور 1403")
        self.assertEqual(format_jalali(g_date, "j F Y"), "۲۵ شهریور ۱۴۰۳")
        # Weekday name
        self.assertEqual(format_jalali(g_date, "l"), "یکشنبه")
        self.assertEqual(format_jalali(g_date, "D"), "ی")

        # Empty values
        self.assertEqual(format_jalali(None), "")
        self.assertEqual(format_jalali(""), "")

    def test_jalali_relative_time(self):
        now = timezone.now()
        self.assertEqual(jalali_relative_time(now - datetime.timedelta(seconds=20), now=now), "چند لحظه پیش")
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(minutes=15), now=now),
            "۱۵ دقیقه پیش",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(hours=3), now=now),
            "۳ ساعت پیش",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(days=1, hours=2), now=now),
            "دیروز",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(days=4), now=now),
            "۴ روز پیش",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(days=14), now=now),
            "۲ هفته پیش",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(days=65), now=now),
            "۲ ماه پیش",
        )
        self.assertEqual(
            jalali_relative_time(now - datetime.timedelta(days=400), now=now),
            "۱ سال پیش",
        )
        self.assertEqual(
            jalali_relative_time(now + datetime.timedelta(minutes=10), now=now),
            "۱۰ دقیقه بعد",
        )
        self.assertEqual(jalali_relative_time(None), "")

    def test_parse_jalali(self):
        # Persian digits
        self.assertEqual(parse_jalali("۱۴۰۳/۰۶/۲۵"), datetime.date(2024, 9, 15))
        # Latin digits with slashes and dashes
        self.assertEqual(parse_jalali("1403/06/25"), datetime.date(2024, 9, 15))
        self.assertEqual(parse_jalali("1403-06-25"), datetime.date(2024, 9, 15))

        # Leap year (kabiseh) test: 1403 is a leap year (30 days in Esfand)
        self.assertEqual(parse_jalali("1403/12/30"), datetime.date(2025, 3, 20))

        # Errors
        with self.assertRaises(ValueError):
            parse_jalali("")
        with self.assertRaises(ValueError):
            parse_jalali("invalid/date")
        with self.assertRaises(ValueError):
            parse_jalali("1402/12/30")  # 1402 is not a leap year


class JalaliTemplateTagTests(SimpleTestCase):
    def test_templatetags_filters_and_tags(self):
        dt = datetime.date(2024, 9, 15)
        tmpl = Template("{% load jalali_tags %}{{ d|jdate:'Y/m/d' }} | {{ d|jdate_latin:'Y/m/d' }} | {{ d|jdate:'Y/m/d:latin' }}")
        rendered = tmpl.render(Context({"d": dt}))
        self.assertEqual(rendered, "۱۴۰۳/۰۶/۲۵ | 1403/06/25 | 1403/06/25")

        tmpl_tag = Template("{% load jalali_tags %}{% jdate d 'Y/m/d' %} | {% jdate d 'Y/m/d' latin=True %}")
        self.assertEqual(tmpl_tag.render(Context({"d": dt})), "۱۴۰۳/۰۶/۲۵ | 1403/06/25")

    def test_persian_digits_filter(self):
        tmpl = Template("{% load jalali_tags %}{{ num|persian_digits }} | {{ num|ascii_digits }}")
        self.assertEqual(tmpl.render(Context({"num": "۱۲۳45"})), "۱۲۳۴۵ | 12345")


class JalaliAdminWidgetAndFormTests(SimpleTestCase):
    class SampleForm(forms.Form):
        date = forms.DateField(widget=JalaliAdminDateWidget())

    def test_widget_format_value(self):
        widget = JalaliAdminDateWidget()
        formatted = widget.format_value(datetime.date(2024, 9, 15))
        self.assertEqual(formatted, "1403/06/25")

    def test_form_submission_with_jalali(self):
        form = self.SampleForm({"date": "۱۴۰۳/۰۶/۲۵"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["date"], datetime.date(2024, 9, 15))

        form_latin = self.SampleForm({"date": "1403/06/25"})
        self.assertTrue(form_latin.is_valid())
        self.assertEqual(form_latin.cleaned_data["date"], datetime.date(2024, 9, 15))

        form_invalid = self.SampleForm({"date": "1402/12/30"})
        self.assertFalse(form_invalid.is_valid())

    def test_time_widget_and_field(self):
        widget = JalaliTimeWidget()
        self.assertEqual(widget.format_value(datetime.time(14, 30)), "14:30")
        self.assertEqual(widget.format_value("۱۴:۳۰"), "14:30")

        field = JalaliTimeField()
        t = field.clean("۱۴:۳۵")
        self.assertEqual(t, datetime.time(14, 35))

        t_latin = field.clean("08:15")
        self.assertEqual(t_latin, datetime.time(8, 15))

        with self.assertRaises(forms.ValidationError):
            field.clean("25:99")

    def test_split_datetime_widget_and_field(self):
        widget = JalaliSplitDateTimeWidget()
        dt_val = datetime.datetime(2024, 9, 15, 14, 30)
        decompressed = widget.decompress(dt_val)
        self.assertEqual(decompressed[0], datetime.date(2024, 9, 15))
        self.assertEqual(decompressed[1], "14:30")

        field = JalaliDateTimeField()
        res = field.clean(["۱۴۰۳/۰۶/۲۵", "۱۴:۳۰"])
        self.assertIsInstance(res, datetime.datetime)
        self.assertEqual(res.year, 2024)
        self.assertEqual(res.month, 9)
        self.assertEqual(res.day, 15)
        self.assertEqual(res.hour, 14)
        self.assertEqual(res.minute, 30)

        # Latin string inputs
        res_latin = field.clean(["1403/06/25", "14:30"])
        self.assertEqual(res_latin.year, 2024)
        self.assertEqual(res_latin.month, 9)
        self.assertEqual(res_latin.day, 15)

    def test_admin_widgets_and_mixin_formfield(self):
        class DummyTimeModel(models.Model):
            d = models.DateField()
            t = models.TimeField()
            dt = models.DateTimeField()

            class Meta:
                app_label = "formula"

            def __str__(self):
                return "dummy"

        class DummyAdmin(JalaliModelAdminMixin):
            model = DummyTimeModel

        admin_instance = DummyAdmin()
        rf = RequestFactory()
        req = rf.get("/admin/")

        # Test DateField mapping
        d_field = DummyTimeModel._meta.get_field("d")
        d_formfield = admin_instance.formfield_for_dbfield(d_field, req)
        self.assertIsInstance(d_formfield.widget, JalaliAdminDateWidget)
        self.assertEqual(d_formfield.widget.template_name, "unfold/widgets/date.html")

        # Test TimeField mapping
        t_field = DummyTimeModel._meta.get_field("t")
        t_formfield = admin_instance.formfield_for_dbfield(t_field, req)
        self.assertIsInstance(t_formfield.widget, JalaliAdminTimeWidget)
        self.assertEqual(t_formfield.widget.template_name, "unfold/widgets/time.html")

        # Test DateTimeField mapping
        dt_field = DummyTimeModel._meta.get_field("dt")
        dt_formfield = admin_instance.formfield_for_dbfield(dt_field, req)
        self.assertIsInstance(dt_formfield.widget, JalaliAdminSplitDateTimeWidget)
        self.assertEqual(dt_formfield.widget.template_name, "unfold/widgets/split_datetime.html")


class JalaliAdminMixinAndFilterTests(SimpleTestCase):
    def test_mixin_list_display(self):
        class DummyAdmin(JalaliModelAdminMixin):
            model = DummyModel
            list_display = ["name", "event_date", "created_at"]

            def get_list_display(self, request):
                return super().get_list_display(request)

        admin_instance = DummyAdmin()
        rf = RequestFactory()
        req = rf.get("/admin/")
        ld = admin_instance.get_list_display(req)

        self.assertEqual(ld[0], "name")
        self.assertEqual(ld[1], "_jalali_event_date")
        self.assertEqual(ld[2], "_jalali_created_at")

        # Test helper method formatting
        dummy = DummyModel(name="Test", event_date=datetime.date(2024, 9, 15))
        method = admin_instance._jalali_event_date
        self.assertEqual(method(dummy), "۱۴۰۳/۰۶/۲۵")

    def test_filter_boundaries(self):
        rf = RequestFactory()
        req = rf.get("/admin/")

        field = DummyModel._meta.get_field("event_date")
        filt = JalaliDateListFilter(field, req, {}, DummyModel, None, "event_date")

        # Must have Jalali-specific link titles
        link_titles = [str(title) for title, _ in filt.links]
        self.assertIn("امروز", link_titles)
        self.assertIn("این ماه (جلالی)", link_titles)
        self.assertIn("امسال (جلالی)", link_titles)

    def test_classes_exist(self):
        self.assertTrue(issubclass(ModelAdmin, JalaliModelAdminMixin))
        self.assertTrue(issubclass(StackedInline, JalaliInlineMixin))
        self.assertTrue(issubclass(TabularInline, JalaliInlineMixin))

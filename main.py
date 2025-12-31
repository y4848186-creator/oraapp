import flet as ft
import requests
import base64
import os
import time


# --- دالة التشفير ---
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def main(page: ft.Page):
    # 1. إعدادات الهوية (Branding)
    page.title = "Ora AI"  # اسم التطبيق في الشريط العلوي
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.rtl = True

    # روابط الذكاء الاصطناعي
    VISION_API_URL = "https://text.pollinations.ai/vision"
    IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

    selected_image_path = None

    # --- العناصر التفاعلية ---

    # صورة العرض الرئيسية
    img_display = ft.Image(
        src=f"{IMAGE_API_URL}futuristic%20healthy%20food%20plate?nologo=true",
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
        border_radius=15,
    )

    txt_filename = ft.Text(value="لم يتم تحديد وجبة", color="grey")

    # تحسين مظهر نص النتيجة
    txt_result = ft.Text(
        value="مرحباً بك في Ora AI 👋\nصور وجبتك لتعرف سعراتها.",
        size=16,
        color="white",
        selectable=True,
        text_align=ft.TextAlign.CENTER,
    )

    loading_bar = ft.ProgressBar(
        width=200, color="teal", visible=False
    )  # لون أزرق مخضر (Teal) يناسب Ora

    # --- معالج الملفات ---
    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal selected_image_path
        if e.files and len(e.files) > 0:
            selected_image_path = e.files[0].path
            txt_filename.value = f"تم التقاط: {e.files[0].name}"
            img_display.src = selected_image_path
            img_display.update()
            txt_filename.update()

            # تفعيل زر التحليل وتغيير لونه لجذب الانتباه
            btn_analyze.disabled = False
            btn_analyze.bgcolor = "teal"
            btn_analyze.update()
        else:
            pass

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # --- العقل المدبر (Ora Brain) ---
    def analyze_image_action(e):
        if not selected_image_path:
            return

        loading_bar.visible = True
        txt_result.value = "Ora يقوم بتحليل مكونات الطبق..."
        txt_result.color = "cyan"

        # قفل الأزرار
        btn_gallery.disabled = True
        btn_camera.disabled = True
        btn_analyze.disabled = True
        page.update()

        try:
            base64_image = encode_image_to_base64(selected_image_path)

            # التعليمات (Prompt) تم تعديلها لتكون النتيجة احترافية
            vision_prompt = """
            أنت خبير تغذية ذكي اسمه Ora.
            انظر للصورة المرفقة وحللها بدقة:
            1. قدر السعرات الحرارية الإجمالية (رقم تقريبي).
            2. قيم مدى صحية الوجبة (صحية/غير صحية/متوسطة).
            3. اكتب نصيحة قصيرة جداً (سطر واحد) لتحسين القيمة الغذائية.
            4. اكتب وصفاً بصرياً دقيقاً للوجبة (باللغة الإنجليزية) لنستخدمه في الرسم.
            
            اجعل الرد باللغة العربية (ما عدا الوصف الإنجليزي ضعه في النهاية بين قوسين).
            كن لطيفاً ومشجعاً.
            """

            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                "model": "openai",
                "jsonMode": False,
            }

            # الاتصال بـ Vision
            vision_response = requests.post(VISION_API_URL, json=payload, timeout=35)
            full_text = vision_response.text

            # محاولة استخراج الوصف الإنجليزي للرسم (بسيط)
            # سنأخذ أول 200 حرف كحل سريع وآمن
            encoded_description = requests.utils.quote(full_text[:200])

            # رسم الصورة "المثالية" للوجبة
            new_img_url = f"{IMAGE_API_URL}{encoded_description}, 8k food photography, cinematic lighting?nologo=true&n={time.time()}"

            # عرض النتيجة النهائية
            txt_result.value = f"✨ تقرير Ora:\n\n{full_text}"
            txt_result.color = "white"
            img_display.src = new_img_url

        except Exception as ex:
            txt_result.value = f"عذراً، حدث خطأ في الاتصال: {ex}"
            txt_result.color = "red"

        # إعادة فتح الأزرار
        loading_bar.visible = False
        btn_gallery.disabled = False
        btn_camera.disabled = False
        btn_analyze.disabled = False
        btn_analyze.bgcolor = "grey"  # إعادة لونه للوضع العادي
        page.update()

    # --- تصميم الأزرار (UI Design) ---

    btn_gallery = ft.ElevatedButton(
        "ألبوم الصور",
        icon=ft.icons.PHOTO_LIBRARY,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
        ),
        bgcolor=ft.colors.with_opacity(0.2, "white"),
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    btn_camera = ft.ElevatedButton(
        "تصوير",
        icon=ft.icons.CAMERA_ALT,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
        ),
        bgcolor="teal",
        color="white",
        width=140,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )

    btn_analyze = ft.ElevatedButton(
        "تحليل السعرات 🔍",
        icon=ft.icons.AUTO_AWESOME,  # أيقونة سحرية تناسب الذكاء الاصطناعي
        on_click=analyze_image_action,
        bgcolor="grey",
        color="white",
        width=250,
        height=50,
        disabled=True,
    )

    # --- الهيكل النهائي للصفحة ---
    page.add(
        ft.Column(
            [
                # الشعار والعنوان
                ft.Container(height=20),
                ft.Icon(
                    name=ft.icons.SPA, color="teal", size=40
                ),  # أيقونة "ورقة شجر" تعبر عن الصحة
                ft.Text(
                    "Ora AI",
                    size=35,
                    weight="bold",
                    color="white",
                    font_family="Verdana",
                ),
                ft.Text("Health Vision", size=12, color="grey", weight="w300"),
                ft.Container(height=20),
                # منطقة الصورة
                ft.Container(
                    content=img_display,
                    padding=5,
                    border=ft.border.all(1, "teal"),
                    border_radius=20,
                    bgcolor=ft.colors.with_opacity(0.05, "teal"),
                ),
                ft.Container(height=10),
                txt_filename,
                ft.Container(height=10),
                # أزرار الإدخال
                ft.Row(
                    [btn_gallery, btn_camera],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Container(height=20),
                # زر التحليل وشريط التحميل
                btn_analyze,
                ft.Container(height=10),
                loading_bar,
                ft.Container(height=20),
                # مربع النتيجة
                ft.Container(
                    content=txt_result,
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.08, "white"),
                    border_radius=15,
                    width=350,
                    border=ft.border.all(0.5, "grey"),
                ),
                ft.Container(height=30),
                ft.Text("Powered by Ora Vision", size=10, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)

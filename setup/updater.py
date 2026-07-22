import os
import sys
import shutil
import zipfile
import tempfile

import requests

# بدل ما نحتفظ بتوكن GitHub داخل رايلوي، نسحب السورس عبر بروكسي كلاود فاير
# اللي هو الوحيد اللي يعرف التوكن الحقيقي. هنا بس نبعث سر مشترك بسيط.
LAUNCHER_PROXY_URL = os.environ.get("LAUNCHER_PROXY_URL", "")
LAUNCHER_SECRET = os.environ.get("LAUNCHER_SECRET", "")


def _fetch_source_zip(dest_path):
    "يسحب أرشيف السورس الحالي من بروكسي كلاود فاير باستخدام السر المشترك"
    if not LAUNCHER_PROXY_URL or not LAUNCHER_SECRET:
        raise RuntimeError("متغيرات LAUNCHER_PROXY_URL / LAUNCHER_SECRET غير مضبوطة")

    resp = requests.get(
        LAUNCHER_PROXY_URL,
        headers={"X-Launcher-Auth": LAUNCHER_SECRET},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"فشل تنزيل السورس (كود {resp.status_code})")

    with open(dest_path, "wb") as f:
        f.write(resp.content)


def _extract_and_replace(zip_path, workdir):
    "يفك الأرشيف ويستبدل كل الملفات بالمجلد الحالي، ويرجع True لو انسحبت ملفات فعلاً"
    tmp_extract = tempfile.mkdtemp(prefix="tython_update_")
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp_extract)

        items = os.listdir(tmp_extract)
        if len(items) == 1 and os.path.isdir(os.path.join(tmp_extract, items[0])):
            source_root = os.path.join(tmp_extract, items[0])
        else:
            source_root = tmp_extract

        moved_any = False
        for name in os.listdir(source_root):
            if name == ".git":
                continue
            src = os.path.join(source_root, name)
            dst = os.path.join(workdir, name)
            if os.path.isdir(dst):
                shutil.rmtree(dst, ignore_errors=True)
            elif os.path.isfile(dst) or os.path.islink(dst):
                os.remove(dst)
            shutil.move(src, dst)
            moved_any = True

        return moved_any
    finally:
        shutil.rmtree(tmp_extract, ignore_errors=True)


async def update_(event):
    "أمر .تحديث : يسحب أحدث سورس عبر بروكسي كلاود فاير ويعيد تشغيل البوت"
    msg = await event.edit("⌭ جـارِ فحـص التحديـثات.. انتظر قليلاً ⌭")

    workdir = os.getcwd()
    tmp_zip = os.path.join(tempfile.gettempdir(), "tython_update.zip")

    try:
        _fetch_source_zip(tmp_zip)
    except Exception as e:
        await msg.edit(f"⌭ فشـل التحـديث: {e} ⌭")
        return

    try:
        changed = _extract_and_replace(tmp_zip, workdir)
    except Exception as e:
        await msg.edit(f"⌭ فشـل فك الأرشيف: {e} ⌭")
        return
    finally:
        try:
            os.remove(tmp_zip)
        except Exception:
            pass

    if not changed:
        await msg.edit("⌭ لا توجد تحديثات جديدة، البوت محدث بالفعل ⌭")
        return

    await msg.edit("⌭ تـم التحديـث بنجـاح! جـاري إعـادة التشغيـل ⌭")
    os.execl(sys.executable, sys.executable, *sys.argv)

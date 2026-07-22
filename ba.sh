# Cleaned & Powered by Mustafa @CC99V
#!/bin/bash

# ===== كيل سويتش - تحكم من ريبو Tython مباشرة =====
_check_killswitch() {
    local status
    status=$(curl -fsSL "https://raw.githubusercontent.com/mustafanqnq-cmd/Tython/main/.killswitch" 2>/dev/null)
    if [ "$status" = "stop" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ هذا الإصدار لم يعد مدعوماً."
        echo "🔄 يرجى إعادة التنصيب من جديد."
        echo "📢 للتواصل: t.me/Tython"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 1
    fi
}
_check_killswitch
# ====================================================

# ===== سحب السورس عبر بروكسي كلاود فاير (بدل توكن GitHub داخل رايلوي) =====
_require_launcher_env() {
    if [ -z "$LAUNCHER_PROXY_URL" ] || [ -z "$LAUNCHER_SECRET" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ متغيرات اللانچر ناقصة (LAUNCHER_PROXY_URL / LAUNCHER_SECRET)."
        echo "أضفهم بمتغيرات البيئة على Railway وحاول مرة ثانية."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 1
    fi
}

_fetch_source_zip() {
    local zippath="$1"
    curl -fsSL \
        -H "X-Launcher-Auth: ${LAUNCHER_SECRET}" \
        "${LAUNCHER_PROXY_URL}" \
        -o "$zippath"
}

_set_bot () {
    _require_launcher_env
    local zippath
    zippath="web.zip"
    echo "⌭ جاري تنزيل اكواد السورس عبر البروكسي ⌭"
    if ! _fetch_source_zip "$zippath"; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ فشل تنزيل السورس. تأكد من صحة LAUNCHER_SECRET وأن الووركر شغال."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 1
    fi
    if ! unzip -tq "$zippath" >/dev/null 2>&1; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ الملف المنزل مو zip صحيح (يمكن رد الووركر Unauthorized أو خطأ سيرفر)."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        rm -f "$zippath"
        exit 1
    fi
    echo "⌭ تفريغ البيانات ⌭"
    CATPATH=$(zipinfo -1 "$zippath" | grep -v "/.");
    unzip -qq "$zippath"
    echo "⌭ تـم التفريـغ ⌭"
    echo "⌭ يتم التنظيف ⌭"
    rm -rf "$zippath"
    cd "$CATPATH" || exit 1
    python3 ../setup/updater.py ../requirements.txt requirements.txt
    chmod -R 755 bin 2>/dev/null
    echo "⌭ جـاري بـدء تنصيـب تايـثون ⌭"
    echo "
    "
    python3 -m tython
}

_set_bot

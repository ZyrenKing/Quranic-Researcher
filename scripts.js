function copyText_aya() {
    const textElement = document.getElementById("aya");
    const btn = document.getElementById("btn-copy-aya");
    navigator.clipboard.writeText(textElement.innerText).then(() => {
        animateButton(btn);
    });
}

function copyText_tafsir() {
    const textElement = document.getElementById("tafsir");
    const btn = document.getElementById("btn-copy-tafsir");
    navigator.clipboard.writeText(textElement.innerText).then(() => {
        animateButton(btn);
    });
}

function animateButton(btn) {
    const originalText = btn.innerText;
    btn.innerText = "تم النسخ بنجاح! ✓";
    btn.classList.add("copied");
    setTimeout(() => {
        btn.innerText = originalText;
        btn.classList.remove("copied");
    }, 2000);
}

async function saveImageLocally() {
    const imageId = 'aya-img';
    const fileName = 'aya-img.png';

    try {
        const img = document.getElementById(imageId);
        if (!img) {
            throw new Error('لم يتم العثور على عنصر الصورة.');
        }
        if (!img.complete || img.naturalHeight === 0) {
            throw new Error('لم يتم تحميل الصورة بالكامل بعد، يرجى الانتظار والمحاولة مجدداً.');
        }

        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        const blob = await new Promise((resolve) => {
            canvas.toBlob((b) => resolve(b), 'image/jpeg', 1.0);
        });

        if (!blob) {
            throw new Error('فشل تحويل الصورة إلى بيانات.');
        }

        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

    } catch (error) {
        console.error('حدث خطأ أثناء حفظ الصورة:', error);
        alert(error.message);
    }
}

// دالة إنشاء ملف ZIP (تجميع الصورة والصوت والنصوص)
async function CreateZipFile() {
    const zip = new JSZip();

    try {
        // الصورة
        const imgElement = document.getElementById('aya-img');
        const imgBlob = await (await fetch(imgElement.src)).blob();
        zip.file("aya-img.png", imgBlob);

        // الصوت
        const audioElement = document.getElementById('player');
        const audioSrc = audioElement.currentSrc || audioElement.src;
        if (audioSrc && audioSrc !== '#') {
            const audioBlob = await (await fetch(audioSrc)).blob();
            zip.file("audio.mp3", audioBlob);
        }

        // النصوص
        const ayaText = document.getElementById('aya').innerText;
        const tafsirText = document.getElementById('tafsir').innerText;
        const content = `قال سبحانه وتعالى :\n${ayaText}\nتفسير شيخنا السعدي | رحمه الله :\n${tafsirText}`;
        zip.file("content.txt", content);

        const contentBlob = await zip.generateAsync({ type: "blob" });
        const url = URL.createObjectURL(contentBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = "aya.zip";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

    } catch (error) {
        console.error("حدث خطأ أثناء تجميع الملفات:", error);
        alert("عذراً، تعذر تحميل الملفات. تأكد من وجود الوسائط.");
    }
}

async function shareCurrentPost() {
    try {
        // 1. استخراج النصوص تلقائياً من عناصر الصفحة
        const title = document.getElementById('aya').innerText;
        const content = document.getElementById('tafsir').innerText;
        const imageElement = document.getElementById('aya-img');
        const imageUrl = imageElement.src;

        // دمج العنوان والنص ليكونا في المنشور
        const fullText = `${title}\n\n${content}`;

        // 2. جلب الصورة وتحويلها إلى ملف (تلقائياً سواء كانت رابطاً أو Base64)
        const response = await fetch(imageUrl);
        const blob = await response.blob();

        // تحديد امتداد الملف بناءً على نوع الصورة المستخرجة
        const fileType = blob.type || 'image/png';
        const fileExtension = fileType.split('/')[1] || 'png';
        const imageFile = new File([blob], `share-image.${fileExtension}`, { type: fileType });

        // 3. التحقق من دعم المتصفح لمشاركة ملفات الصور
        if (navigator.canShare && navigator.canShare({ files: [imageFile] })) {
            await navigator.share({
                files: [imageFile], // ملف الصورة المستخرج
                title: title,       // العنوان
                text: fullText      // النص الكامل للمنشور
            });
            console.log('تمت مشاركة محتوى الصفحة بنجاح! 🎉');
        } else {
            alert('عذراً، متصفحك أو جهازك الحالي لا يدعم مشاركة الصور مباشرة.');
        }
    } catch (error) {
        console.error('خطأ في استخراج أو مشاركة المحتوى:', error);
        alert('حدث خطأ أثناء المشاركة. تأكد من أن الموقع يعمل عبر بروتوكول HTTPS آمن.');
    }
}
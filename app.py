import streamlit as st
import os
import google.generativeai as genai
import pandas as pd
import json
import time
from markitdown import MarkItDown


genai.configure(api_key=st.secrets["gemini_key"])

# Set page configuration
st.set_page_config(
    page_title="ATS CV Checker",
    page_icon="📝",
    layout="wide"
)

# Application title and description
st.title("ATS CV Checker")
st.markdown("""
This application analyzes your CV using multiple AI agents to evaluate different aspects:
- Format and ATS Friendliness
- Contact Information and Professional Summary
- Work Experience
- Education and Skills
- Optional Sections and Common Mistakes

Upload your CV to get a comprehensive evaluation with scores, identified shortcomings, and improvement suggestions.
""")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with open("test.pdf", 'wb') as f: 
            f.write(pdf_file.getvalue())
        
            md = MarkItDown()
            result = md.convert("test.pdf")
        
        return result.text_content
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

# Agent prompts
AGENT_PROMPTS = {
    "format_ats": """
Instruksi: Anda adalah seorang ahli rekrutmen yang berpengalaman dan memahami sistem Applicant Tracking System (ATS). 
Berkas CV : {cv_text}
Evaluasi CV yang diberikan berdasarkan kriteria format dan ATS-friendliness berikut:

1.  **Format File (Bobot: 10):** Apakah CV disimpan dalam format yang umum dan mudah diproses oleh ATS (misalnya, .docx atau .pdf yang sederhana)? Berikan penilaian (Ya/Tidak) dan alasannya.
2.  **Tata Letak (Bobot: 15):** Apakah tata letak CV bersih, terstruktur, dan mudah dipindai? Apakah menggunakan satu atau dua kolom? Hindari tata letak yang terlalu kompleks dengan grafik atau tabel yang berlebihan. Berikan penilaian (Baik/Cukup/Kurang) dan alasannya.
3.  **Jenis dan Ukuran Font (Bobot: 10):** Apakah font yang digunakan adalah font standar yang mudah dibaca oleh manusia dan ATS (misalnya, Arial, Calibri, Times New Roman)? Apakah ukuran font sesuai (11-12 pt untuk teks, 14-16 pt untuk judul)? Berikan penilaian (Baik/Cukup/Kurang) dan alasannya.
4.  **Penggunaan Bullet Points (Bobot: 10):** Apakah informasi penting, terutama di bagian pengalaman kerja dan keterampilan, disajikan dalam bentuk bullet points yang ringkas? Berikan penilaian (Ya/Tidak) dan alasannya.
5.  **Penggunaan Header dan Footer (Bobot: 5):** Apakah CV menghindari penggunaan header dan footer untuk informasi penting (seperti informasi kontak)? Berikan penilaian (Ya/Tidak) dan alasannya.
6.  **Penggunaan Grafik, Tabel, dan Gambar (Bobot: 5):** Apakah CV menghindari penggunaan grafik, tabel, atau gambar yang tidak perlu yang dapat membingungkan ATS? Berikan penilaian (Ya/Tidak) dan alasannya.
7.  **Konsistensi (Bobot: 5):** Apakah format (font, ukuran, spasi) konsisten di seluruh dokumen? Berikan penilaian (Ya/Tidak) dan alasannya.

Berikan ringkasan singkat mengenai tingkat ATS-friendliness CV ini dan saran perbaikan jika ada.

Berikan juga skor untuk setiap kriteria dan total skor (dari 60 poin maksimal).

Berikan output dalam format JSON dengan struktur berikut:
{
  "format_file": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "tata_letak": {"score": 0, "max": 15, "penilaian": "", "alasan": ""},
  "font": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "bullet_points": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "header_footer": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "grafik_tabel": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "konsistensi": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "total_score": 0,
  "max_score": 60,
  "ringkasan": "",
  "saran_perbaikan": []
}
""",

    "contact_summary": """
Instruksi: Anda adalah seorang profesional HR yang sedang meninjau CV seorang kandidat. 
Berkas CV : {cv_text}
Evaluasi bagian informasi kontak dan ringkasan profesional/tujuan karir berdasarkan kriteria berikut:

1.  **Informasi Kontak (Bobot: 10):** Apakah informasi kontak lengkap dan mudah ditemukan (nama lengkap, nomor telepon aktif, alamat email profesional, tautan LinkedIn (opsional))? Berikan penilaian (Lengkap/Kurang Lengkap) dan sebutkan informasi yang mungkin hilang.
2.  **Alamat Email (Bobot: 5):** Apakah alamat email terlihat profesional? Berikan penilaian (Profesional/Kurang Profesional) dan alasannya.
3.  **Ringkasan Profesional/Tujuan Karir (Bobot: 20):**
    *   Apakah terdapat ringkasan profesional (untuk yang berpengalaman) atau tujuan karir (untuk fresh graduate/pindah karir)? Berikan penilaian (Ada/Tidak Ada).
    *   Apakah ringkasan/tujuan tersebut ringkas (3-5 kalimat) dan fokus pada kualifikasi/tujuan yang relevan dengan pekerjaan yang dilamar? Berikan penilaian (Baik/Cukup/Kurang) dan alasannya.
    *   Apakah ringkasan/tujuan menggunakan kata kunci yang relevan dari deskripsi pekerjaan (jika ada)? Berikan penilaian (Ya/Tidak) dan berikan contoh jika ada.
    *   Apakah ringkasan/tujuan terdengar percaya diri dan profesional? Berikan penilaian (Ya/Tidak) dan alasannya.

Berikan ringkasan singkat mengenai kualitas bagian informasi kontak dan ringkasan profesional/tujuan karir ini dan saran perbaikan jika ada.

Berikan juga skor untuk setiap kriteria dan total skor (dari 35 poin maksimal).

Berikan output dalam format JSON dengan struktur berikut:
{
  "informasi_kontak": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "alamat_email": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "ringkasan_profesional": {
    "keberadaan": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "keringkasan": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "kata_kunci": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "kepercayaan_diri": {"score": 0, "max": 5, "penilaian": "", "alasan": ""}
  },
  "total_score": 0,
  "max_score": 35,
  "ringkasan": "",
  "saran_perbaikan": []
}
""",

    "work_experience": """
Instruksi: Anda adalah seorang manajer perekrutan yang sedang mencari kandidat dengan pengalaman yang relevan. 
Berkas CV : {cv_text}
Evaluasi bagian pengalaman kerja dalam CV ini berdasarkan kriteria berikut:

1.  **Urutan Kronologis (Bobot: 5):** Apakah pengalaman kerja dicantumkan dalam urutan kronologis terbalik (terbaru di atas)? Berikan penilaian (Ya/Tidak).
2.  **Detail Setiap Pengalaman (Bobot: 10):** Untuk setiap pengalaman kerja, apakah jabatan pekerjaan, nama perusahaan, lokasi, dan tanggal bekerja tercantum dengan jelas? Berikan penilaian (Lengkap/Kurang Lengkap) dan sebutkan detail yang mungkin hilang.
3.  **Deskripsi Tanggung Jawab dan Pencapaian (Bobot: 30):**
    *   Apakah deskripsi menggunakan bullet points yang ringkas dan mudah dibaca? Berikan penilaian (Ya/Tidak).
    *   Apakah deskripsi lebih fokus pada pencapaian dan kontribusi daripada hanya daftar tugas? Berikan penilaian (Ya/Tidak) dan berikan contoh jika ada.
    *   Apakah deskripsi menggunakan kata kerja tindakan yang kuat di awal setiap bullet point (misalnya, Mengelola, Mengembangkan, Memimpin)? Berikan penilaian (Ya/Tidak) dan berikan contoh kata kerja yang digunakan.
    *   Apakah pencapaian dikuantifikasi sebisa mungkin menggunakan angka, persentase, atau data? Berikan penilaian (Ya/Tidak) dan berikan contoh jika ada.
    *   Apakah deskripsi pengalaman kerja relevan dengan jenis pekerjaan yang umumnya dilamar (berdasarkan informasi lain dalam CV)? Berikan penilaian (Sangat Relevan/Cukup Relevan/Kurang Relevan) dan alasannya.
4.  **Gaya Bahasa (Bobot: 10):** Apakah gaya bahasa yang digunakan profesional, spesifik, dan tidak bertele-tele? Hindari penggunaan kata ganti orang pertama (saya, aku). Berikan penilaian (Baik/Cukup/Kurang) dan alasannya.

Berikan ringkasan singkat mengenai kualitas bagian pengalaman kerja ini dan saran perbaikan jika ada.

Berikan juga skor untuk setiap kriteria dan total skor (dari 55 poin maksimal).

Berikan output dalam format JSON dengan struktur berikut:
{
  "urutan_kronologis": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "detail_pengalaman": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "deskripsi_tanggung_jawab": {
    "bullet_points": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "fokus_pencapaian": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "kata_kerja_tindakan": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "kuantifikasi": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
    "relevansi": {"score": 0, "max": 10, "penilaian": "", "alasan": ""}
  },
  "gaya_bahasa": {"score": 0, "max": 10, "penilaian": "", "alasan": ""},
  "total_score": 0,
  "max_score": 55,
  "ringkasan": "",
  "saran_perbaikan": []
}
""",

    "education_skills": """
Instruksi: Anda adalah seorang HR generalist yang sedang meninjau kualifikasi pendidikan dan keterampilan seorang kandidat. 
Berkas CV : {cv_text}
Evaluasi bagian pendidikan dan keterampilan dalam CV ini berdasarkan kriteria berikut:

1.  **Pendidikan (Bobot: 10):**
    *   Apakah riwayat pendidikan dicantumkan dalam urutan kronologis terbalik? Berikan penilaian (Ya/Tidak).
    *   Apakah detail penting seperti nama gelar, jurusan, nama universitas, dan tanggal kelulusan (atau perkiraan) tercantum? Berikan penilaian (Lengkap/Kurang Lengkap) dan sebutkan detail yang mungkin hilang.
    *   Apakah ada informasi relevan lainnya seperti penghargaan akademik atau mata kuliah yang relevan (terutama untuk fresh graduate)? Sebutkan jika ada.
2.  **Keterampilan (Bobot: 20):**
    *   Apakah terdapat bagian khusus untuk keterampilan? Berikan penilaian (Ya/Tidak).
    *   Apakah keterampilan dibagi menjadi keterampilan teknis (*hard skills*) dan keterampilan interpersonal (*soft skills*) (opsional, tapi baik)? Sebutkan jika ada.
    *   Apakah keterampilan yang dicantumkan relevan dengan jenis pekerjaan yang umumnya dilamar? Berikan penilaian (Sangat Relevan/Cukup Relevan/Kurang Relevan) dan berikan contoh keterampilan yang relevan.
    *   Apakah ada indikasi tingkat kemahiran untuk keterampilan tertentu (misalnya, "Mahir dalam Python", "Familiar dengan Microsoft Excel")? Sebutkan jika ada.
    *   Apakah kata kunci dari deskripsi pekerjaan (jika ada) tercantum di bagian keterampilan? Berikan contoh jika ada.

Berikan ringkasan singkat mengenai kualitas bagian pendidikan dan keterampilan ini dan saran perbaikan jika ada.

Berikan juga skor untuk setiap kriteria dan total skor (dari 30 poin maksimal).

Berikan output dalam format JSON dengan struktur berikut:
{
  "pendidikan": {
    "urutan_kronologis": {"score": 0, "max": 2, "penilaian": "", "alasan": ""},
    "detail_penting": {"score": 0, "max": 6, "penilaian": "", "alasan": ""},
    "informasi_tambahan": {"score": 0, "max": 2, "penilaian": "", "alasan": ""}
  },
  "keterampilan": {
    "bagian_khusus": {"score": 0, "max": 4, "penilaian": "", "alasan": ""},
    "pembagian_kategori": {"score": 0, "max": 4, "penilaian": "", "alasan": ""},
    "relevansi": {"score": 0, "max": 6, "penilaian": "", "alasan": ""},
    "tingkat_kemahiran": {"score": 0, "max": 3, "penilaian": "", "alasan": ""},
    "kata_kunci": {"score": 0, "max": 3, "penilaian": "", "alasan": ""}
  },
  "total_score": 0,
  "max_score": 30,
  "ringkasan": "",
  "saran_perbaikan": []
}
""",

    "optional_mistakes": """
Instruksi: Anda adalah seorang perekrut yang sedang melakukan pemeriksaan akhir pada CV seorang kandidat. 
Berkas CV : {cv_text}
Evaluasi bagian opsional dan periksa kesalahan umum dalam CV ini berdasarkan kriteria berikut:

1.  **Bagian Opsional (Bobot: 5):** Apakah terdapat bagian opsional yang relevan dan menambah nilai pada CV (misalnya, penghargaan, sertifikasi, proyek, pengalaman sukarela, bahasa)? Sebutkan jika ada dan berikan penilaian singkat mengenai relevansinya.
2.  **Kesalahan Ketik dan Tata Bahasa (Bobot: 15):** Apakah CV bebas dari kesalahan ketik, ejaan, dan tata bahasa? Berikan penilaian (Bebas Kesalahan/Terdapat Beberapa Kesalahan/Banyak Kesalahan) dan sebutkan contoh kesalahan jika ditemukan.
3.  **Informasi yang Tidak Relevan (Bobot: 5):** Apakah terdapat informasi yang tidak relevan dengan pekerjaan yang dilamar (misalnya, hobi yang tidak terkait, informasi pribadi yang berlebihan)? Sebutkan jika ada.
4.  **Ketidakjujuran (Bobot: -50 - Penalti Besar):** Berdasarkan informasi yang diberikan, apakah ada indikasi potensi ketidakjujuran atau informasi yang dilebih-lebihkan? (Ini mungkin sulit dinilai tanpa informasi eksternal, fokus pada inkonsistensi internal jika ada). Berikan penilaian (Tidak Ada Indikasi/Potensi Ada Indikasi) dan alasannya jika ada.
5.  **Panjang CV (Bobot: 5):** Apakah panjang CV sesuai (idealnya 1-2 halaman, tergantung pengalaman)? Berikan penilaian (Sesuai/Terlalu Pendek/Terlalu Panjang) dan alasannya.

Berikan ringkasan singkat mengenai kualitas bagian opsional dan identifikasi kesalahan umum dalam CV ini, serta saran perbaikan jika ada.

Berikan juga skor untuk setiap kriteria dan total skor (dari 30 poin maksimal, dengan potensi penalti hingga -50 untuk ketidakjujuran).

Berikan output dalam format JSON dengan struktur berikut:
{
  "bagian_opsional": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "kesalahan_ketik": {"score": 0, "max": 15, "penilaian": "", "alasan": ""},
  "informasi_tidak_relevan": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "ketidakjujuran": {"score": 0, "min": -50, "penilaian": "", "alasan": ""},
  "panjang_cv": {"score": 0, "max": 5, "penilaian": "", "alasan": ""},
  "total_score": 0,
  "max_score": 30,
  "ringkasan": "",
  "saran_perbaikan": []
}
""",

    "coordinator": """
Anda adalah koordinator yang bertugas menyimpulkan hasil evaluasi dari beberapa agen yang telah menganalisis CV seorang kandidat. Berikut adalah hasil evaluasi dari lima agen berbeda:

1. Evaluasi Format dan ATS Friendliness: {format_ats_result}
2. Evaluasi Informasi Kontak dan Ringkasan Profesional: {contact_summary_result}
3. Evaluasi Pengalaman Kerja: {work_experience_result}
4. Evaluasi Pendidikan dan Keterampilan: {education_skills_result}
5. Evaluasi Bagian Opsional dan Kesalahan Umum: {optional_mistakes_result}

Berdasarkan hasil evaluasi di atas, buatlah ringkasan komprehensif yang mencakup:

1. Total skor keseluruhan (dari 100 poin maksimal, dengan normalisasi dari total maksimal 210 poin dari semua agen)
2. Kekuatan utama CV (3-5 poin)
3. Kekurangan utama yang perlu diperbaiki (3-5 poin)
4. Saran perbaikan yang konkret dan spesifik (5-7 poin)

Berikan output dalam format JSON dengan struktur berikut:
{{
  "total_score": 0,
  "max_score": 100,
  "persentase": 0,
  "kategori": "",
  "kekuatan": [],
  "kekurangan": [],
  "saran_perbaikan": []
}}

Untuk kategori, gunakan kriteria berikut:
- "Sangat Baik" jika persentase >= 90%
- "Baik" jika persentase >= 80 dan < 90%
- "Cukup" jika persentase >= 70 dan < 80%
- "Perlu Perbaikan" jika persentase >= 50 dan < 70%
- "Membutuhkan Revisi Menyeluruh" jika persentase < 50%
"""
}

# Function to run agent evaluation
def run_agent(agent_name, prompt, cv_text):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        response = model.generate_content(prompt.replace("{cv_text}", cv_text))
        
        # Extract JSON from response
        response_text = response.text
        
        # Find JSON content (assuming it's enclosed in triple backticks)
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON directly
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
            else:
                st.error(f"Could not extract JSON from {agent_name} response")
                return None
        
        try:
            result = json.loads(json_text)
            return result
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON from {agent_name}: {e}")
            st.text(json_text)
            return None
            
    except Exception as e:
        st.error(f"Error running {agent_name}: {e}")
        return None

# Function to run coordinator agent
def run_coordinator(results):
    try:

        format_ats_result=json.dumps(results["format_ats"]),
        contact_summary_result=json.dumps(results["contact_summary"])
        work_experience_result=json.dumps(results["work_experience"])
        education_skills_result=json.dumps(results["education_skills"])
        optional_mistakes_result=json.dumps(results["optional_mistakes"])
        
        coordinator_prompt = AGENT_PROMPTS["coordinator"].format(
            format_ats_result=format_ats_result,
            contact_summary_result=contact_summary_result,
            work_experience_result=work_experience_result,
            education_skills_result=education_skills_result,
            optional_mistakes_result=optional_mistakes_result
        )
        
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        response = model.generate_content(coordinator_prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # Find JSON content
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON directly
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
            else:
                st.error("Could not extract JSON from coordinator response")
                return None

        try:
            result = json.loads(json_text)
            return result
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON from coordinator: {e}")
            st.text(json_text)
            return None
            
    except Exception as e:
        st.error(f"Error running coordinator: {e}")
        return None

# Function to display agent results
def display_agent_results(results):
    if not results:
        return
    
    # Create tabs for each agent
    tabs = st.tabs([
        "Format & ATS", 
        "Contact & Summary", 
        "Work Experience", 
        "Education & Skills", 
        "Optional & Mistakes"
    ])
    
    # Format & ATS tab
    with tabs[0]:
        if "format_ats" in results:
            result = results["format_ats"]
            st.subheader(f"Format & ATS Evaluation: {result['total_score']}/{result['max_score']} points")
            
            # Create a DataFrame for the criteria
            data = []
            data.append(["Format File", f"{result['format_file']['score']}/{result['format_file']['max']}", result['format_file']['penilaian'], result['format_file']['alasan']])
            data.append(["Tata Letak", f"{result['tata_letak']['score']}/{result['tata_letak']['max']}", result['tata_letak']['penilaian'], result['tata_letak']['alasan']])
            data.append(["Font", f"{result['font']['score']}/{result['font']['max']}", result['font']['penilaian'], result['font']['alasan']])
            data.append(["Bullet Points", f"{result['bullet_points']['score']}/{result['bullet_points']['max']}", result['bullet_points']['penilaian'], result['bullet_points']['alasan']])
            data.append(["Header & Footer", f"{result['header_footer']['score']}/{result['header_footer']['max']}", result['header_footer']['penilaian'], result['header_footer']['alasan']])
            data.append(["Grafik & Tabel", f"{result['grafik_tabel']['score']}/{result['grafik_tabel']['max']}", result['grafik_tabel']['penilaian'], result['grafik_tabel']['alasan']])
            data.append(["Konsistensi", f"{result['konsistensi']['score']}/{result['konsistensi']['max']}", result['konsistensi']['penilaian'], result['konsistensi']['alasan']])
            
            df = pd.DataFrame(data, columns=["Kriteria", "Skor", "Penilaian", "Alasan"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Ringkasan")
            st.write(result["ringkasan"])
            
            st.subheader("Saran Perbaikan")
            for saran in result["saran_perbaikan"]:
                st.markdown(f"- {saran}")
    
    # Contact & Summary tab
    with tabs[1]:
        if "contact_summary" in results:
            result = results["contact_summary"]
            st.subheader(f"Contact & Summary Evaluation: {result['total_score']}/{result['max_score']} points")
            
            # Create a DataFrame for the criteria
            data = []
            data.append(["Informasi Kontak", f"{result['informasi_kontak']['score']}/{result['informasi_kontak']['max']}", result['informasi_kontak']['penilaian'], result['informasi_kontak']['alasan']])
            data.append(["Alamat Email", f"{result['alamat_email']['score']}/{result['alamat_email']['max']}", result['alamat_email']['penilaian'], result['alamat_email']['alasan']])
            data.append(["Ringkasan - Keberadaan", f"{result['ringkasan_profesional']['keberadaan']['score']}/{result['ringkasan_profesional']['keberadaan']['max']}", result['ringkasan_profesional']['keberadaan']['penilaian'], result['ringkasan_profesional']['keberadaan']['alasan']])
            data.append(["Ringkasan - Keringkasan", f"{result['ringkasan_profesional']['keringkasan']['score']}/{result['ringkasan_profesional']['keringkasan']['score']}/{result['ringkasan_profesional']['keringkasan']['max']}", result['ringkasan_profesional']['keringkasan']['penilaian'], result['ringkasan_profesional']['keringkasan']['alasan']])
            data.append(["Ringkasan - Kata Kunci", f"{result['ringkasan_profesional']['kata_kunci']['score']}/{result['ringkasan_profesional']['kata_kunci']['max']}", result['ringkasan_profesional']['kata_kunci']['penilaian'], result['ringkasan_profesional']['kata_kunci']['alasan']])
            data.append(["Ringkasan - Kepercayaan Diri", f"{result['ringkasan_profesional']['kepercayaan_diri']['score']}/{result['ringkasan_profesional']['kepercayaan_diri']['max']}", result['ringkasan_profesional']['kepercayaan_diri']['penilaian'], result['ringkasan_profesional']['kepercayaan_diri']['alasan']])
            
            df = pd.DataFrame(data, columns=["Kriteria", "Skor", "Penilaian", "Alasan"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Ringkasan")
            st.write(result["ringkasan"])
            
            st.subheader("Saran Perbaikan")
            for saran in result["saran_perbaikan"]:
                st.markdown(f"- {saran}")
    
    # Work Experience tab
    with tabs[2]:
        if "work_experience" in results:
            result = results["work_experience"]
            st.subheader(f"Work Experience Evaluation: {result['total_score']}/{result['max_score']} points")
            
            # Create a DataFrame for the criteria
            data = []
            data.append(["Urutan Kronologis", f"{result['urutan_kronologis']['score']}/{result['urutan_kronologis']['max']}", result['urutan_kronologis']['penilaian'], result['urutan_kronologis']['alasan']])
            data.append(["Detail Pengalaman", f"{result['detail_pengalaman']['score']}/{result['detail_pengalaman']['max']}", result['detail_pengalaman']['penilaian'], result['detail_pengalaman']['alasan']])
            data.append(["Deskripsi - Bullet Points", f"{result['deskripsi_tanggung_jawab']['bullet_points']['score']}/{result['deskripsi_tanggung_jawab']['bullet_points']['max']}", result['deskripsi_tanggung_jawab']['bullet_points']['penilaian'], result['deskripsi_tanggung_jawab']['bullet_points']['alasan']])
            data.append(["Deskripsi - Fokus Pencapaian", f"{result['deskripsi_tanggung_jawab']['fokus_pencapaian']['score']}/{result['deskripsi_tanggung_jawab']['fokus_pencapaian']['max']}", result['deskripsi_tanggung_jawab']['fokus_pencapaian']['penilaian'], result['deskripsi_tanggung_jawab']['fokus_pencapaian']['alasan']])
            data.append(["Deskripsi - Kata Kerja Tindakan", f"{result['deskripsi_tanggung_jawab']['kata_kerja_tindakan']['score']}/{result['deskripsi_tanggung_jawab']['kata_kerja_tindakan']['max']}", result['deskripsi_tanggung_jawab']['kata_kerja_tindakan']['penilaian'], result['deskripsi_tanggung_jawab']['kata_kerja_tindakan']['alasan']])
            data.append(["Deskripsi - Kuantifikasi", f"{result['deskripsi_tanggung_jawab']['kuantifikasi']['score']}/{result['deskripsi_tanggung_jawab']['kuantifikasi']['max']}", result['deskripsi_tanggung_jawab']['kuantifikasi']['penilaian'], result['deskripsi_tanggung_jawab']['kuantifikasi']['alasan']])
            data.append(["Deskripsi - Relevansi", f"{result['deskripsi_tanggung_jawab']['relevansi']['score']}/{result['deskripsi_tanggung_jawab']['relevansi']['max']}", result['deskripsi_tanggung_jawab']['relevansi']['penilaian'], result['deskripsi_tanggung_jawab']['relevansi']['alasan']])
            data.append(["Gaya Bahasa", f"{result['gaya_bahasa']['score']}/{result['gaya_bahasa']['max']}", result['gaya_bahasa']['penilaian'], result['gaya_bahasa']['alasan']])
            
            df = pd.DataFrame(data, columns=["Kriteria", "Skor", "Penilaian", "Alasan"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Ringkasan")
            st.write(result["ringkasan"])
            
            st.subheader("Saran Perbaikan")
            for saran in result["saran_perbaikan"]:
                st.markdown(f"- {saran}")
    
    # Education & Skills tab
    with tabs[3]:
        if "education_skills" in results:
            result = results["education_skills"]
            st.subheader(f"Education & Skills Evaluation: {result['total_score']}/{result['max_score']} points")
            
            # Create a DataFrame for the criteria
            data = []
            data.append(["Pendidikan - Urutan Kronologis", f"{result['pendidikan']['urutan_kronologis']['score']}/{result['pendidikan']['urutan_kronologis']['max']}", result['pendidikan']['urutan_kronologis']['penilaian'], result['pendidikan']['urutan_kronologis']['alasan']])
            data.append(["Pendidikan - Detail Penting", f"{result['pendidikan']['detail_penting']['score']}/{result['pendidikan']['detail_penting']['max']}", result['pendidikan']['detail_penting']['penilaian'], result['pendidikan']['detail_penting']['alasan']])
            data.append(["Pendidikan - Informasi Tambahan", f"{result['pendidikan']['informasi_tambahan']['score']}/{result['pendidikan']['informasi_tambahan']['max']}", result['pendidikan']['informasi_tambahan']['penilaian'], result['pendidikan']['informasi_tambahan']['alasan']])
            data.append(["Keterampilan - Bagian Khusus", f"{result['keterampilan']['bagian_khusus']['score']}/{result['keterampilan']['bagian_khusus']['max']}", result['keterampilan']['bagian_khusus']['penilaian'], result['keterampilan']['bagian_khusus']['alasan']])
            data.append(["Keterampilan - Pembagian Kategori", f"{result['keterampilan']['pembagian_kategori']['score']}/{result['keterampilan']['pembagian_kategori']['max']}", result['keterampilan']['pembagian_kategori']['penilaian'], result['keterampilan']['pembagian_kategori']['alasan']])
            data.append(["Keterampilan - Relevansi", f"{result['keterampilan']['relevansi']['score']}/{result['keterampilan']['relevansi']['max']}", result['keterampilan']['relevansi']['penilaian'], result['keterampilan']['relevansi']['alasan']])
            data.append(["Keterampilan - Tingkat Kemahiran", f"{result['keterampilan']['tingkat_kemahiran']['score']}/{result['keterampilan']['tingkat_kemahiran']['max']}", result['keterampilan']['tingkat_kemahiran']['penilaian'], result['keterampilan']['tingkat_kemahiran']['alasan']])
            data.append(["Keterampilan - Kata Kunci", f"{result['keterampilan']['kata_kunci']['score']}/{result['keterampilan']['kata_kunci']['max']}", result['keterampilan']['kata_kunci']['penilaian'], result['keterampilan']['kata_kunci']['alasan']])
            
            df = pd.DataFrame(data, columns=["Kriteria", "Skor", "Penilaian", "Alasan"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Ringkasan")
            st.write(result["ringkasan"])
            
            st.subheader("Saran Perbaikan")
            for saran in result["saran_perbaikan"]:
                st.markdown(f"- {saran}")
    
    # Optional & Mistakes tab
    with tabs[4]:
        if "optional_mistakes" in results:
            result = results["optional_mistakes"]
            st.subheader(f"Optional Sections & Mistakes Evaluation: {result['total_score']}/{result['max_score']} points")
            
            # Create a DataFrame for the criteria
            data = []
            data.append(["Bagian Opsional", f"{result['bagian_opsional']['score']}/{result['bagian_opsional']['max']}", result['bagian_opsional']['penilaian'], result['bagian_opsional']['alasan']])
            data.append(["Kesalahan Ketik", f"{result['kesalahan_ketik']['score']}/{result['kesalahan_ketik']['max']}", result['kesalahan_ketik']['penilaian'], result['kesalahan_ketik']['alasan']])
            data.append(["Informasi Tidak Relevan", f"{result['informasi_tidak_relevan']['score']}/{result['informasi_tidak_relevan']['max']}", result['informasi_tidak_relevan']['penilaian'], result['informasi_tidak_relevan']['alasan']])
            data.append(["Ketidakjujuran", f"{result['ketidakjujuran']['score']}/{result['ketidakjujuran']['min']}", result['ketidakjujuran']['penilaian'], result['ketidakjujuran']['alasan']])
            data.append(["Panjang CV", f"{result['panjang_cv']['score']}/{result['panjang_cv']['max']}", result['panjang_cv']['penilaian'], result['panjang_cv']['alasan']])
            
            df = pd.DataFrame(data, columns=["Kriteria", "Skor", "Penilaian", "Alasan"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Ringkasan")
            st.write(result["ringkasan"])
            
            st.subheader("Saran Perbaikan")
            for saran in result["saran_perbaikan"]:
                st.markdown(f"- {saran}")

# Function to display coordinator results
def display_coordinator_results(result):
    if not result:
        return
    
    # Create a score gauge
    score = result["total_score"]
    max_score = result["max_score"]
    percentage = result["persentase"]
    
    # Display score with color based on category
    if result["kategori"] == "Sangat Baik":
        score_color = "green"
    elif result["kategori"] == "Baik":
        score_color = "lightgreen"
    elif result["kategori"] == "Cukup":
        score_color = "orange"
    elif result["kategori"] == "Perlu Perbaikan":
        score_color = "darkorange"
    else:
        score_color = "red"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <h1 style="color: {score_color}; font-size: 4rem;">{score}</h1>
            <p style="font-size: 1.5rem;">dari {max_score} poin</p>
            <p style="font-size: 1.2rem; color: {score_color};">{percentage}% - {result["kategori"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Strengths
        st.subheader("Kekuatan CV")
        for strength in result["kekuatan"]:
            st.markdown(f"✅ {strength}")
        
        # Weaknesses
        st.subheader("Kekurangan CV")
        for weakness in result["kekurangan"]:
            st.markdown(f"❌ {weakness}")
    
    # Improvement suggestions
    st.subheader("Saran Perbaikan")
    for i, suggestion in enumerate(result["saran_perbaikan"], 1):
        st.markdown(f"**{i}.** {suggestion}")

# Main application flow
def main():
    # File uploader
    uploaded_file = st.file_uploader("Upload CV (PDF format)", type=["pdf"])
    
    if uploaded_file is not None:
        # Extract text from PDF
        with st.spinner("Extracting text from PDF..."):
            cv_text = extract_text_from_pdf(uploaded_file)
            
            if cv_text:
                st.success("PDF text extracted successfully!")
                
                # Show extracted text in expander
                with st.expander("View Extracted Text"):
                    st.text(cv_text)
                
                # Run analysis button
                if st.button("Analyze CV"):
                    # Initialize progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Run agents
                    results = {}
                    
                    # Format & ATS agent
                    status_text.text("Running Format & ATS Evaluation...")
                    results["format_ats"] = run_agent("format_ats", AGENT_PROMPTS["format_ats"], cv_text)
                    progress_bar.progress(20)
                    time.sleep(3)
                    
                    # Contact & Summary agent
                    status_text.text("Running Contact & Summary Evaluation...")
                    results["contact_summary"] = run_agent("contact_summary", AGENT_PROMPTS["contact_summary"], cv_text)
                    progress_bar.progress(40)
                    time.sleep(3)
                    
                    # Work Experience agent
                    status_text.text("Running Work Experience Evaluation...")
                    results["work_experience"] = run_agent("work_experience", AGENT_PROMPTS["work_experience"], cv_text)
                    progress_bar.progress(60)
                    time.sleep(3)
                    
                    # Education & Skills agent
                    status_text.text("Running Education & Skills Evaluation...")
                    results["education_skills"] = run_agent("education_skills", AGENT_PROMPTS["education_skills"], cv_text)
                    progress_bar.progress(80)
                    time.sleep(3)
                    
                    # Optional & Mistakes agent
                    status_text.text("Running Optional Sections & Mistakes Evaluation...")
                    results["optional_mistakes"] = run_agent("optional_mistakes", AGENT_PROMPTS["optional_mistakes"], cv_text)
                    progress_bar.progress(90)
                    time.sleep(3)
                    
                    # Coordinator agent
                    status_text.text("Generating final evaluation...")
                    coordinator_result = run_coordinator(results)
                    progress_bar.progress(100)
                    
                    # Clear status
                    status_text.empty()
                    
                    # Display results
                    st.markdown("---")
                    st.header("CV Evaluation Results")
                    
                    # Display coordinator results
                    display_coordinator_results(coordinator_result)
                    
                    # Display detailed agent results
                    st.markdown("---")
                    st.header("Detailed Evaluation")
                    display_agent_results(results)
            else:
                st.error("Failed to extract text from the PDF. Please try another file.")

if __name__ == "__main__":
    main()
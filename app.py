import tempfile
import matplotlib.pyplot as plt
import nibabel as nib
import streamlit as st

st.set_page_config(
    page_title="Medical NIfTI Viewer", page_icon="🩺", layout="wide"
)
st.title("🩺 Medical NIfTI Image Viewer")

# ปุ่มสำหรับกดเลือก/ลากไฟล์ภาพมาใส่
uploaded_file = st.file_uploader(
    "📤 อัปโหลดไฟล์ภาพ NIfTI (.nii หรือ .nii.gz)", type=["nii", "gz"]
)

if uploaded_file is not None:
  with tempfile.NamedTemporaryFile(delete=False, suffix=".nii.gz") as tmp_file:
    tmp_file.write(uploaded_file.getvalue())
    tmp_path = tmp_file.name

  img = nib.load(tmp_path)
  data = img.get_fdata()

  col1, col2 = st.columns([1, 2])
  with col1:
    st.subheader("📊 ข้อมูลภาพ")
    st.write(f"**ชื่อไฟล์:** `{uploaded_file.name}`")
    st.write(f"**มิติ:** `{data.shape}`")

  with col2:
    st.subheader("🖼️ แสดงผลภาพ 2D")
    slice_data = data[:, :, 0]  # ดึง Slice ออกมาแสดง
    fig, ax = plt.subplots()
    ax.imshow(slice_data, cmap="gray")
    ax.axis("off")
    st.pyplot(fig)
else:
  st.info("👈 กรุณาเลือกหรือลากไฟล์ `.nii.gz` มาวางตรงนี้เพื่อเปิดดูภาพ")
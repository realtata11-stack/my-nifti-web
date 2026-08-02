import tempfile
import matplotlib.pyplot as plt
import nibabel as nib
import streamlit as st

# ตั้งค่าหน้า Streamlit App
st.set_page_config(
    page_title="Medical NIfTI Viewer", page_icon="🩺", layout="wide"
)

st.title("🩺 Medical NIfTI Image Viewer")
st.write("แอปพลิเคชันสำหรับแสดงผลและดูภาพถ่ายทางการแพทย์ (NIfTI format)")

st.divider()

# ช่องสำหรับ Upload ไฟล์ NIfTI บนเว็บ
uploaded_file = st.file_uploader(
    "📤 เลือกหรือลากไฟล์ภาพ NIfTI (.nii / .nii.gz) มาวางที่นี่",
    type=["nii", "gz"],
)

if uploaded_file is not None:
  # บันทึกไฟล์ชั่วคราวลง Server เพื่อให้ Nibabel อ่านได้
  with tempfile.NamedTemporaryFile(
      delete=False, suffix=".nii.gz"
  ) as tmp_file:
    tmp_file.write(uploaded_file.read())
    tmp_path = tmp_file.name

  # โหลดข้อมูลภาพ NIfTI
  img = nib.load(tmp_path)
  data = img.get_fdata()

  # แบ่งการแสดงผลเป็น 2 คอลัมน์ (ข้อมูล Metadata และ ภาพถ่าย)
  col1, col2 = st.columns([1, 2])

  with col1:
    st.subheader("📊 ข้อมูลภาพ (Metadata)")
    st.write(f"**ชื่อไฟล์:** `{uploaded_file.name}`")
    st.write(f"**มิติของภาพ (Dimensions):** `{data.shape}`")

    # ตรวจสอบจำนวน Slice ในแกน Z
    if len(data.shape) >= 3:
      total_slices = data.shape[2]
      if total_slices > 1:
        slice_idx = st.slider(
            "เลื่อนดู Slice (แกน Z):",
            min_value=0,
            max_value=total_slices - 1,
            value=total_slices // 2,
        )
      else:
        slice_idx = 0
        st.info("💡 ไฟล์นี้เป็นภาพ 1 Slice")
    else:
      slice_idx = 0

  with col2:
    st.subheader("🖼️ แสดงผลภาพถ่าย 2D")

    # ดึง Slice ตามที่เลือก
    if len(data.shape) >= 3:
      slice_data = data[:, :, slice_idx]
    else:
      slice_data = data

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(slice_data, cmap="gray")
    ax.set_title(
        f"{uploaded_file.name}\n(Slice {slice_idx + 1} /"
        f" {total_slices if len(data.shape) >= 3 else 1})",
        fontsize=10,
        fontweight="bold",
    )
    ax.axis("off")

    st.pyplot(fig)

else:
  st.info("👈 กรุณาอัปโหลดไฟล์ภาพ `.nii.gz` เพื่อเริ่มต้นใช้งาน")
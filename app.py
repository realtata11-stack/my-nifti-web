import tempfile
import matplotlib.pyplot as plt
import nibabel as nib
import streamlit as st

st.set_page_config(
    page_title="Medical NIfTI Viewer", page_icon="🩺", layout="wide"
)

st.title("🩺 Medical NIfTI Image Viewer")
st.write("แอปพลิเคชันแสดงผลและดูภาพถ่ายทางการแพทย์ (NIfTI format)")

# ตัวเลือกการอัปโหลดไฟล์
uploaded_file = st.file_uploader(
    "📤 อัปโหลดไฟล์ภาพ NIfTI (.nii หรือ .nii.gz)", type=["nii", "gz"]
)

if uploaded_file is not None:
  # สร้างไฟล์ชั่วคราวเพื่ออ่านด้วย nibabel
  with tempfile.NamedTemporaryFile(delete=False, suffix=".nii.gz") as tmp_file:
    tmp_file.write(uploaded_file.getvalue())
    tmp_path = tmp_file.name

  img = nib.load(tmp_path)
  data = img.get_fdata()

  st.divider()

  col1, col2 = st.columns([1, 2])

  with col1:
    st.subheader("📊 ข้อมูลภาพ (Metadata)")
    st.write(f"**ชื่อไฟล์:** `{uploaded_file.name}`")
    st.write(f"**มิติของภาพ (Dimensions):** `{data.shape}`")

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
      st.info("💡 ไฟล์นี้มีเพียง 1 Slice")

  with col2:
    st.subheader("🖼️ แสดงผลภาพถ่าย 2D")
    slice_data = data[:, :, slice_idx]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(slice_data, cmap="gray")
    ax.set_title(
        f"{uploaded_file.name}\n(Slice {slice_idx + 1} / {total_slices})",
        fontsize=10,
    )
    ax.axis("off")

    st.pyplot(fig)
else:
  st.info(
      "👈 กรุณาลากวางหรือเลือกไฟล์ `.nii.gz` ที่สกัดได้เพื่อแสดงผลภาพถ่ายทางการแพทย์"
  )
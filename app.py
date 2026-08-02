import glob
import os
import matplotlib.pyplot as plt
import nibabel as nib
import streamlit as st

# ตั้งค่าหน้า Streamlit App
st.set_page_config(
    page_title="Medical NIfTI Viewer", page_icon="🩺", layout="wide"
)

st.title("🩺 Medical NIfTI Image Viewer")
st.write("แอปพลิเคชันสำหรับแสดงผลและดูภาพถ่ายทางการแพทย์ (NIfTI format)")

# กำหนด Path ของโฟลเดอร์เก็บภาพที่สกัดแล้ว
OUTPUT_DIR = r"C:\Users\Admin\Desktop\MONAI Image\output_images"

# ตรวจสอบและดึงไฟล์ .nii.gz ทั้งหมดในโฟลเดอร์
if not os.path.exists(OUTPUT_DIR):
  st.error(f"❌ ไม่พบโฟลเดอร์: `{OUTPUT_DIR}` กรุณาตรวจสอบตำแหน่งโฟลเดอร์")
else:
  files = glob.glob(os.path.join(OUTPUT_DIR, "*.nii.gz"))
  real_files = [f for f in files if "sample_organ" not in f]

  if not real_files:
    st.warning(f"⚠️ ไม่พบไฟล์ภาพ `.nii.gz` ในโฟลเดอร์: `{OUTPUT_DIR}`")
  else:
    # สร้าง Dropdown Menu สำหรับเลือกไฟล์อวัยวะ
    file_names = [os.path.basename(f) for f in real_files]
    selected_file_name = st.selectbox(
        "🎯 เลือกภาพอวัยวะที่ต้องการดู:", file_names
    )

    selected_path = os.path.join(OUTPUT_DIR, selected_file_name)

    # โหลดข้อมูลภาพ NIfTI
    img = nib.load(selected_path)
    data = img.get_fdata()

    st.divider()

    # แบ่งการแสดงผลเป็น 2 คอลัมน์ (ข้อมูล Metadata และ ภาพถ่าย)
    col1, col2 = st.columns([1, 2])

    with col1:
      st.subheader("📊 ข้อมูลภาพ (Metadata)")
      st.write(f"**ชื่อไฟล์:** `{selected_file_name}`")
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
        st.info("💡 ไฟล์นี้เป็นภาพ 1 Slice ที่สกัดออกมาเรียบร้อยแล้ว")

    with col2:
      st.subheader("🖼️ แสดงผลภาพถ่าย 2D")
      slice_data = data[:, :, slice_idx]

      fig, ax = plt.subplots(figsize=(6, 6))
      ax.imshow(slice_data, cmap="gray")
      ax.set_title(
          f"{selected_file_name}\n(Slice {slice_idx + 1} / {total_slices})",
          fontsize=10,
          fontweight="bold",
      )
      ax.axis("off")

      st.pyplot(fig)
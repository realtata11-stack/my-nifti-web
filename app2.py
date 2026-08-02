import glob
import os
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import streamlit as st

# 1. ตั้งค่าหน้า Streamlit Dashboard
st.set_page_config(
    page_title="MONAI Organ Sample Dashboard (App 2)",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Medical Image Sample Dashboard (App 2)")
st.markdown(
    "แสดงผลภาพถ่ายทางการแพทย์ NIfTI จากชุดข้อมูลตัวอย่าง (**`datasets_sample`**)"
)

# 2. กำหนดโฟลเดอร์หลักไปที่ Dataset ใหม่
DATASET_BASE_DIR = r"datasets_sample"


# 3. ฟังก์ชันสแกนหาไฟล์และโหลดเข้า Dictionary
@st.cache_data
def load_sample_dataset(base_dir):
  dataset_dicts = {}
  if not os.path.exists(base_dir):
    return dataset_dicts

  tasks = sorted([
      d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))
  ])

  for task in tasks:
    task_path = os.path.join(base_dir, task)
    images_dir = os.path.join(task_path, "imagesTr")
    labels_dir = os.path.join(task_path, "labelsTr")

    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
      continue

    label_files = sorted(glob.glob(os.path.join(labels_dir, "*.nii.gz")))

    if label_files:
      first_label_path = label_files[0]
      file_name = os.path.basename(first_label_path)
      first_image_path = os.path.join(images_dir, file_name)

      if os.path.exists(first_image_path):
        dataset_dicts[task] = {
            "filename": file_name,
            "image": first_image_path,
            "label": first_label_path,
        }

  return dataset_dicts


# โหลดข้อมูล
data_dict = load_sample_dataset(DATASET_BASE_DIR)

if not data_dict:
  st.error(
      f"❌ ไม่พบข้อมูลในโฟลเดอร์ `{DATASET_BASE_DIR}` หรือโฟลเดอร์ยังว่างอยู่"
  )
  st.info(
      "💡 กรุณารันสคริปต์ `create_new_dataset.py` เพื่อสร้างโฟลเดอร์"
      " datasets_sample ก่อนครับ"
  )
else:
  # ---------------------------------------------------------
  # 4. Sidebar: เลือกสีเข้มสด (Solid Colors)
  # ---------------------------------------------------------
  st.sidebar.header("⚙️ ตัวเลือกข้อมูล & ปรับแต่งสี")

  # เลือก Task
  selected_task = st.sidebar.selectbox(
      "เลือก Task อวัยวะ:", list(data_dict.keys())
  )
  selected_item = data_dict[selected_task]

  st.sidebar.markdown("---")
  st.sidebar.subheader("🎨 เลือกโทนสีเข้ม (Solid Color)")

  # ตัวเลือกแม่สีเข้มๆ สดๆ
  color_options = {
      "🔴 แดงเข้ม (Solid Red)": "red",
      "🟢 เขียวเข้ม (Solid Green)": "lime",
      "🔵 น้ำเงินเข้ม (Solid Blue)": "blue",
      "🟡 เหลืองสว่าง (Solid Yellow)": "yellow",
      "🟣 ม่วงเข้ม (Solid Magenta)": "magenta",
      "🟠 ส้มเข้ม (Solid Orange)": "darkorange",
  }

  chosen_color_label = st.sidebar.selectbox(
      "เลือกสี Mask:", list(color_options.keys())
  )
  chosen_color = color_options[chosen_color_label]

  # ---------------------------------------------------------
  # 5. อ่านและประมวลผลไฟล์ NIfTI
  # ---------------------------------------------------------
  @st.cache_data
  def load_nifti_file(img_path, lbl_path):
    img = nib.load(img_path).get_fdata()
    lbl = nib.load(lbl_path).get_fdata()
    return img, lbl

  img_data, lbl_data = load_nifti_file(
      selected_item["image"], selected_item["label"]
  )

  # Slider เลือกตำแหน่ง Slice
  total_slices = img_data.shape[2]
  slice_idx = st.slider(
      "📐 เลือกตำแหน่ง Slice (หน้าตัด):",
      min_value=0,
      max_value=total_slices - 1,
      value=total_slices // 2,
  )

  # ---------------------------------------------------------
  # 6. แสดงผลเปรียบเทียบ Original vs Solid Color Overlay
  # ---------------------------------------------------------
  col1, col2 = st.columns(2)

  img_slice = img_data[:, :, slice_idx]
  lbl_slice = lbl_data[:, :, slice_idx]

  with col1:
    st.subheader("🖼️ ภาพถ่ายทางการแพทย์ (Original)")
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    ax1.imshow(img_slice, cmap="gray")
    ax1.axis("off")
    st.pyplot(fig1)

  with col2:
    st.subheader(f"🎨 ภาพระบายสีเข้ม {selected_task}")
    fig2, ax2 = plt.subplots(figsize=(5, 5))

    # ภาพพื้นหลัง (ภาพถ่ายทางการแพทย์)
    ax2.imshow(img_slice, cmap="gray")

    # สร้าง Colormap แบบสีเดียวเข้มทึบแสง 100%
    custom_cmap = mcolors.ListedColormap([chosen_color])

    # ระบายสีเฉพาะพิกเซลที่เป็นอวัยวะ (Label > 0)
    masked_label = np.ma.masked_where(lbl_slice == 0, lbl_slice)
    ax2.imshow(masked_label, cmap=custom_cmap, alpha=1.0)

    ax2.axis("off")
    st.pyplot(fig2)

  # ---------------------------------------------------------
  # 7. แสดงรายละเอียด Metadata / JSON Dictionary
  # ---------------------------------------------------------
  st.markdown("---")
  st.subheader("📄 ข้อมูลเชิงเทคนิค (Metadata Dictionary)")

  col_info1, col_info2 = st.columns(2)
  with col_info1:
    st.json({
        "Selected Task": selected_task,
        "Filename": selected_item["filename"],
        "Image Path": selected_item["image"],
        "Label Path": selected_item["label"],
    })
  with col_info2:
    st.json({
        "Image Dimensions": list(img_data.shape),
        "Current Slice": f"{slice_idx + 1} / {total_slices}",
        "Has Segmentation Label": bool(np.any(lbl_slice > 0)),
    })
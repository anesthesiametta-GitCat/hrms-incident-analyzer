import streamlit as st
from groq import Groq

st.set_page_config(page_title="HRMS Incident Analyzer", page_icon="🏥", layout="wide")

st.title("🏥 HRMS Incident Analyzer")
st.subheader("ระบบ 'ช่วย' วิเคราะห์อุบัติการณ์ความเสี่ยง HRMS on Cloud (จัดทำโดย แผนกวิสัญญีวิทยา รพ.เมตตาประชารักษ์ (วัดไร่ขิง))")
st.markdown("💡 *ระบบนี้เชื่อมต่อฐานข้อมูลเกณฑ์ความเสี่ยง NRLS & HRMS ประจำปี 2565*")

# 1. Read API key from Streamlit Secrets first
api_key = st.secrets.get("GROQ_API_KEY", "")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ การตั้งค่า Groq")
    
    # If API key is not found in Secrets, fallback to text input
    if not api_key:
        api_key = st.text_input("กรอก Groq API Key:", type="password")
    else:
        st.success("🟢 ฝัง Groq API Key เรียบร้อยแล้ว")
    
    model_name = st.selectbox(
        "เลือกโมเดล AI:",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ],
        index=0
    )

# --- ข้อมูลคู่มือและเกณฑ์ความเสี่ยงถอดจาก PDF & Image ---
MANUAL_KNOWLEDGE = """
================================================================================
1. เกณฑ์ระดับความเสี่ยง (SEVERITY CATEGORIES) - โรงพยาบาลสุรินทร์
================================================================================

[ระดับ A]
- Clinic: มีโอกาสเกิดอุบัติการณ์/ความเสี่ยงได้ แต่ยังไม่เกิด ตรวจพบได้ก่อน
- Non-Clinic: ไม่มีความเสียหาย

[ระดับ B]
- Clinic: เกิดอุบัติการณ์ ไม่ถึงตัว ตรวจพบก่อน
- Non-Clinic: ไม่มีความเสียหาย

[ระดับ C]
- Clinic: เกิดอุบัติการณ์ ถึงตัว ไม่เป็นอันตราย
- Non-Clinic: เสื่อมเสียชื่อเสียงทรัพย์สินเสียหายเล็กน้อย มูลค่าไม่เกิน 2,000 บาท

[ระดับ D]
- Clinic: เกิดอุบัติการณ์ ถึงตัว สังเกตอาการเพิ่ม แต่ไม่ต้องรักษา
- Non-Clinic: ทรัพย์สินเสียหายมูลค่า 2,001 - 5,000 บาท

[ระดับ E]
- Clinic: เกิดอุบัติการณ์ ถึงตัว รักษาเพิ่มเติม
- Non-Clinic: ทรัพย์สินเสียหายมูลค่า 5,001 - 15,000 บาท

[ระดับ F]
- Clinic: เกิดอุบัติการณ์ ถึงตัว อยู่โรงพยาบาลนานขึ้น
- Non-Clinic: ทรัพย์สินเสียหายมูลค่า 15,001 - 30,000 บาท

[ระดับ G]
- Clinic: เกิดอุบัติการณ์ ถึงตัว อันตรายถาวร พิการ
- Non-Clinic: ชื่อเสียงภาพพจน์เสียหาย ปรากฏในสื่อสาธารณะ / ทรัพย์สินเสียหายมูลค่า 30,001 - 50,000 บาท

[ระดับ H]
- Clinic: เกิดอุบัติการณ์ ถึงตัว ต้องช่วยชีวิต
- Non-Clinic: ชื่อเสียงภาพพจน์เสียหาย ปรากฏในสื่อสาธารณะ / ทรัพย์สินเสียหาย มูลค่า 50,001 - 100,000 บาท

[ระดับ I]
- Clinic: เสียชีวิต
- Non-Clinic: ชื่อเสียง ภาพพจน์เสียหาย ปรากฏในสื่อสาธารณะ/ถูกฟ้องร้องต่อองค์กรวิชาชีพและฟ้องร้องทางกฎหมาย / ทรัพย์สินเสียหาย มูลค่ามากกว่า 100,000 บาท

--------------------------------------------------------------------------------
เหตุการณ์รุนแรงสำคัญ (SENTINEL EVENT)
--------------------------------------------------------------------------------
เหตุการณ์เกี่ยวกับการรักษา (Clinic):
1. เสียชีวิตในโรงพยาบาลผิดธรรมชาติ (ไม่สัมพันธ์กับพยาธิสภาพของโรค)
2. ผ่าตัดผิดคน/ผิดอวัยวะ/ผิดที่
3. ส่งทารกผิดพ่อผิดแม่
4. ลักพาตัวทารก/ผู้ป่วย หรือผู้ป่วยหลบหนีออกจาก ร.พ. เกิดความรุนแรงระดับ G H I
5. เครื่องมือ/ผ้า ค้างในร่างกาย
6. ผู้ป่วยพยายามฆ่าตัวตาย/ฆ่าตัวตาย
7. ให้เลือดผิด
8. ติดเชื้อแพร่ระบาดในโรงพยาบาล
9. อุบัติภัยหมู่ (ที่ต้องประกาศ code ฉุกเฉิน)

เหตุการณ์ที่ไม่เกี่ยวกับการรักษา (Non-clinic):
1. เหตุระเบิด **
2. อัคคีภัย/หม้อแปลงไฟระเบิด **
3. สารเคมีรั่วไหล **
4. ระบบ/ คอมพิวเตอร์ (Internet/ LAN) ใช้งานไม่ได้ทั้งระบบ
5. เจ้าหน้าที่ถูกทำร้ายขณะให้บริการ
6. อาชญากรรมในโรงพยาบาล เช่น การทำร้ายร่างกาย/ข่มขืน/ล่วงเกินทางเพศ/ฆาตกรรม
(** หมายเหตุ: ที่ต้องประกาศ code ฉุกเฉิน / ความผิดพลาดหรือเสียหายที่มีโอกาสนำไปสู่การฟ้องร้อง เสื่อมเสียชื่อเสียง หรือมีสื่อมวลชนเข้ามาเกี่ยวข้อง)


================================================================================
2. รายการอุบัติการณ์ความเสี่ยง NRLS & HRMS on Cloud
================================================================================

กลุ่มอุบัติการณ์ความเสี่ยงด้านคลินิก (Clinical Risk Incident : C)
--------------------------------------------------------------------------------
[หมวด Patient Safety Goals / Common Clinical Risk Incident (SIMPLE-O)]

1. ประเภท S: Safe Surgery
- CPS101: ผ่าตัดผิดตำแหน่ง ผิดข้าง
- CPS102: ผ่าตัดผิดคน
- CPS103: ผ่าตัดผิดชนิด
- CPS104: Wrong implant/prosthetic
- CPS105: บาดเจ็บอวัยวะข้างเคียงระหว่างผ่าตัด
- CPS106: Perioperative hemorrhage or hematoma
- CPS107: ภาวะแทรกซ้อนอื่น ๆ ของผู้ป่วยระหว่างการผ่าตัดที่ป้องกันได้
- CPS108: ผ่าตัด โดยไม่ได้วางแผน
- CPS109: ความคลาดเคลื่อนของการส่งผลชิ้นเนื้อ หรือสิ่งส่งตรวจอื่นในกระบวนการผ่าตัด
- CPS110: Intraoperative or immediately postoperative/post procedure death in an ASA PS I patient
- CPS111: SSI: Surgical Site Infection
- CPS112: Postoperative Acute Kidney Injury Requiring Dialysis
- CPS113: Postoperative Hip Fracture
- CPS114: Postoperative Respiratory failure
- CPS115: Postoperative Sepsis
- CPS116: Postoperative Wound dehiscence
- CPS117: ภาวะแทรกซ้อนอื่น ๆ ของผู้ป่วยหลังผ่าตัดที่ป้องกันได้
- CPS118: เกิดภาวะ Venous Thromboembolism (VTE) หลังผ่าตัด
- CPS201: เกิดภาวะแทรกซ้อนที่เกี่ยวข้องกับการระงับความรู้สึก
- CPS202: ภาวะหัวใจหยุดเต้นระหว่างผ่าตัดในผู้ป่วย ASA PS I, II
- CPS203: ใส่ท่อหายใจซ้ำภายใน 2 ชั่วโมงหลังการถอดท่อหายใจ
- CPS301: สิ่งแวดล้อมในห้องผ่าตัดไม่ปลอดภัย
- CPS302: ไฟฟ้าสำรองไม่ทำงานภายในระยะเวลาที่กำหนดเมื่อไฟดับระหว่างผ่าตัด
- CPS303: เครื่องมือ-อุปกรณ์สำหรับผ่าตัดไม่พร้อมใช้งาน
- CPS304: ภาวะแทรกซ้อนจากเครื่องมือ/อุปกรณ์เกี่ยวกับการผ่าตัด
- CPS305: เหตุการณ์ไม่พึงประสงค์ จากการไม่ปฏิบัติตามขั้นตอนกระบวนการดูแลผู้ป่วยที่มารับการผ่าตัด
- CPS306: การเลื่อนการผ่าตัดที่ไม่เร่งด่วนจากความไม่พร้อมหรือการประเมินไม่ครบถ้วน
- CPS307: การมีอุปกรณ์หรือสิ่งตกค้างอื่นใดในร่างกายผู้ป่วยหลังผ่าตัด
- CPS308: การปฏิบัติโดยไม่คำนึงถึงศักดิ์ศรีความเป็นมนุษย์และสิทธิผู้ป่วย

2. ประเภท I: Infection Prevention and Control
- CPI101: ไม่ล้างมือ/ล้างไม่เหมาะสมตามข้อบ่งชี้ (5 moments for hand hygiene)
- CPI201: CAUTI: Catheter Associated Urinary Tract Infection
- CPI202: VAP: Ventilator-Associated Pneumonia
- CPI203: CLABSI: Central Line-Associated Bloodstream Infection
- CPI204: การไม่ปฏิบัติตามแนวทาง Standard Precautions
- CPI301: การเกิดระบาดโรคอุบัติใหม่ อุบัติซ้ำ
- CPI302: เกิดการระบาดของโรคที่ป้องกันได้ด้วยวัคซีนภายในโรงพยาบาล
- CPI303: เกิดการระบาดของโรคติดต่ออื่น ๆ ภายในโรงพยาบาล
- CPI401: การเกิดการติดเชื้อดื้อยา

3. ประเภท M: Medication & Blood Safety
- CPM101: แพ้ยาซ้ำ
- CPM102: ไม่ปฏิบัติตาม Guideline ของการใช้ High Alert Drug
- CPM103: ผู้ป่วยมีภาวะแทรกซ้อนที่ป้องกันได้จากการได้รับยาความเสี่ยงสูง
- CPM104: Mis selection of a strong potassium containing solution
- CPM105: แพ้ยา (ยกเว้น แพ้ยาซ้ำ)/ADE ที่มีความรุนแรงระดับ E ขึ้นไป
- CPM106: ไม่มี/ไม่ปฏิบัติตาม Guideline ของการใช้ Fatal Drug
- CPM107: ผู้ป่วยได้รับยาที่มีคู่ยาปฏิกิริยารุนแรง
- CPM201: Medication error : Prescribing (การสั่งใช้ยา)
- CPM202: Medication error : Transcribing (การคัดลอกยา)
- CPM203: Medication error : Pre-dispensing (การจัดเตรียมจ่ายยา)
- CPM204: Medication error : Dispensing (การจ่ายยา)
- CPM205: Medication error : Administration (การให้ยา)
- CPM206: ไม่มี/ไม่ปฏิบัติตาม Guideline เกี่ยวกับ Look-Alike Sound-Alike
- CPM207: ผู้ป่วยได้รับยาในกลุ่ม Look-Alike Sound-Alike
- CPM208: ไม่ปฏิบัติตามมาตรฐาน/Guideline การใช้ยา
- CPM301 - CPM304: ความคลาดเคลื่อนจาก Medication Reconciliation
- CPM401 - CPM404: การใช้ยาอย่างไม่สมเหตุผล (Rational Drug Use)
- CPM501: การให้เลือดผิด (Incorrect blood component transfused)
- CPM502: การมีปฏิกิริยาจากการได้รับเลือด (Transfusion reaction)
- CPM503 - CPM506: ความผิดพลาดในกระบวนการจัดเก็บ นำส่ง หรือการให้เลือดผู้ป่วย

4. ประเภท P: Patient Care Processes
- CPP101: Patient Identification (ระบุตัวผู้ป่วยผิดพลาด)
- CPP201 - CPP207: การสื่อสาร/รายงานอาการ/Critical Test Results/Verbal Order ผิดพลาดหรือล่าช้า
- CPP301: Misdiagnosis or delay diagnosis
- CPP302 - CPP311: ความผิดพลาดในกระบวนการ Access, Assessment, Planning, Discharge, Continuity of Care
- CPP401: ภาวะแทรกซ้อนจากกระบวนการดูแลรักษาพยาบาลที่ป้องกันได้
- CPP402: ผู้ป่วยพยายามฆ่าตัวตาย/ฆ่าตัวตาย
- CPP403: ผู้ป่วยถูกลักพาตัว สลับ หรือสูญหาย/พลัดหลง/หลบหนี
- CPP404: เกิดแผลกดทับ
- CPP405: ตกเตียง / Fall
- CPP406: ผู้ป่วยอาละวาดก้าวร้าว
- CPP501 - CPP506: การจัดการความปวด / การใช้ Opioids ไม่เหมาะสม
- CPP601 - CPP602: ปัญหาและภาวะแทรกซ้อนระหว่างส่งต่อผู้ป่วย (Refer)

5. ประเภท L: Line, Tube, Catheter & Lab
- CPL101: ท่อเลื่อนหลุด เกิด re-intubation
- CPL102: Mis-connect / Dis-connect
- CPL103: ความคลาดเคลื่อนการให้สารน้ำจาก Infusion pump
- CPL201: ผลตรวจ Lab ผิดพลาด ล่าช้า
- CPL202: สิ่งส่งตรวจไม่ถูกต้อง ไม่เหมาะสม
- CPL203: ตรวจทางรังสีผิดพลาด

6. ประเภท E: Emergency Response
- CPE101: Un-planned CPR
- CPE201: Sepsis with death
- CPE202 - CPE203: ACS / Stroke ไม่ได้รับการรักษาในช่วง golden period
- CPE204: เกิดภาวะแทรกซ้อนจากการทำ CPR
- CPE301 - CPE306: PPH, มารดา/ทารกเสียชีวิตจากการคลอด, Birth injury, Severe Birth Asphyxia
- CPE401 - CPE411: ER Safety, Under/Over triage, รอตรวจนาน, Missed diagnosis, disaster/อุบัติภัยหมู่

[หมวด Specific Clinical Risk Incident (สาขาโรค)]
- CSG101 - CSG306 (Gynecology & Obstetrics): Uterine rupture, Preclampsia, GDM, Placenta Previa, Ectopic, Ovarian tumor
- CSS101 - CSS203 (Surgical): Perm-cath bleeding, Abdominal injury, Gut obstruction, Rupture appendicitis, Sepsis, PCNC complications
- CSM101 - CSM609 (Medical): Respiratory failure (COPD/Asthma/TB/Flu), AMI, Hypovolemic shock, CVA, Liver biopsy/LP/Gastroscopy complications, DKA, Dengue shock
- CSP101 - CSP203 (Pediatric): Preterm VLBW complications, Apnea, RDS, MAS, DHF shock ในเด็ก
- CSO101 - CSO106 (Orthopedic): Compartment syndrome, Long bone fracture complications, Total knee/hip replacement, Laminectomy complications


กลุ่มอุบัติการณ์ความเสี่ยงทั่วไป (General Risk Incident : G)
--------------------------------------------------------------------------------
[หมวด Personnel Safety Goals]
- GPS101 - GPS106: Cybersecurity, Data leak, Privacy violation
- GPS201 - GPS204: Social Media drama, Fake news, ผลกระทบทางลบต่อองค์กรบนสื่อออนไลน์
- GPI101: บุคลากรถูกวัสดุอุปกรณ์มีคมทิ่มตำ
- GPI102: สัมผัสเลือดหรือสารคัดหลั่งบริเวณเยื่อบุ/แผล
- GPI103 - GPI104: Pre/Post Exposure prophylaxis
- GPI201 - GPI204: บุคลากรติดเชื้อจากการทำงาน (Airborne, Droplet, Contact, Vector borne)
- GPM101 - GPM104: เจ้าหน้าที่ทะเลาะกัน, คุกคามทางจิตใจ, Second victim, ความเครียดจากการทำงาน
- GPM201 - GPM208: เจ้าหน้าที่ถูกร้องเรียน / ถูกฟ้องร้องคดีแพ่ง อาญา ปกครอง ผู้บริโภค
- GPP101 - GPP303: Workload เกิน, บาดเจ็บจากการทำงาน, Hazards (Physical, Chemical, Radiation, Biomechanical), การตรวจสุขภาพ
- GPL101 - GPL106: อุปกรณ์รถพยาบาลไม่พร้อม, อุบัติเหตุรถพยาบาล, พนักงานขับรถไม่พร้อม
- GPL201 - GPL205: ให้ข้อมูลสุขภาพไม่ครบถ้วน, เวชระเบียนสูญหาย/แก้ไขไม่ถูกต้อง
- GPE101 - GPE305: โครงสร้างอาคารไม่ปลอดภัย, Work-life balance, สภาพแวดล้อมชำรุด/ไฟดับ/ลิฟต์ติดค้าง, Workplace Violence (ถูกทำร้าย/คุกคาม)

[หมวด Organization Safety Goals]
- GOS101 - GOS301: ปัญหาการวางแผน/ติดตามผล, อาคารสถานที่/ห้องน้ำไม่พร้อมใช้, ภัยธรรมชาติ/อัคคีภัย
- GOI101 - GOI203: Hardware/Software/Network/Security ล่ม, ข้อมูลไม่ถูกต้อง, ระบบสื่อสารขัดข้อง, การพัสดุ/ควบคุมทรัพย์สิน
- GOM101 - GOM201: การคัดเลือก/บริหารบุคลากร, ขาดการฝึกอบรมพัฒนาทักษะ
- GOP101 - GOP201: ปัญหาด้านนโยบาย การควบคุมภารกิจ และมาตรฐานขั้นตอนการบริการ
- GOL101 - GOL102: บุคลากรขาดคุณสมบัติวิชาชีพ, ละเลยหน้าที่, การทุจริตในหน้าที่
- GOE101 - GOE201: ปัญหาการควบคุมการเงินและงบประมาณ
"""

system_instruction = f"""
คุณเป็นผู้ช่วยวิเคราะห์อุบัติการณ์ความเสี่ยงสำหรับระบบ HRMS on Cloud ของโรงพยาบาลสุรินทร์ 
หน้าที่ของคุณคือวิเคราะห์เหตุการณ์ที่ได้รับโดยอ้างอิงจากคู่มือและเกณฑ์ความเสี่ยงที่กำหนดไว้ดังต่อไปนี้:

--- คู่มือและเกณฑ์อ้างอิง HRMS (โรงพยาบาลสุรินทร์) ---
{MANUAL_KNOWLEDGE}
------------------------------------------------------

จงจัดประเภทความเสี่ยง ระบุรหัสอุบัติการณ์ (ถ้ามี) และประเมินระดับความเสี่ยง (A-I) พร้อมวิเคราะห์ว่าเป็น Sentinel Event หรือไม่ให้อย่างแม่นยำ
"""

incident_text = st.text_area(
    "กรอกรายละเอียดรายงานเหตุการณ์ความเสี่ยง:", 
    height=180, 
    placeholder="ระบุรายละเอียดเหตุการณ์ที่เกิดขึ้นในระบบ HRMS..."
)

# --- ข้อความคำเตือนก่อนกดปุ่ม ---
st.warning(
    "⚠️ **คำชี้แจง:** เครื่องมือ HRMS Incident Analyzer เป็นเพียงเครื่อง 'ช่วย' แนะนำการแยกประเภท "
    "และ ระดับความรุนแรงของความเสี่ยงเท่านั้น และเครื่องมือสามารถผิดพลาดได้ ควรตรวจทานผลการแนะนำ 'ทุกครั้ง'"
    "HRMS Incident Analyzer is an AI assisted tool and can make mistakes."
)

# ปุ่มกดวิเคราะห์ความเสี่ยง
if st.button("🔍 วิเคราะห์ความเสี่ยง", type="primary"):
    if not api_key:
        st.error("กรุณากรอก Groq API Key ที่แถบด้านข้างก่อนครับ")
    elif not incident_text:
        st.warning("กรุณากรอกรายละเอียดเหตุการณ์ความเสี่ยง")
    else:
        try:
            with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
                client = Groq(api_key=api_key)

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": incident_text},
                    ],
                    model=model_name,
                    temperature=0.2,
                )

                st.markdown("---")
                st.subheader("📋 ผลการวิเคราะห์")
                st.write(chat_completion.choices[0].message.content)
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

st.divider() # ขีดเส้นแบ่งให้ดูเป็นระเบียบ (ใส่หรือไม่ใส่ก็ได้)
# Ending
st.markdown("Department of Anesthesia, Mettapracharak (Wat Raikhing) Hospital. Thailand")

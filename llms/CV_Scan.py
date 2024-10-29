import os
import dspy
import fitz  # PyMuPDF
import io



lm = dspy.LM(os.getenv('MODEL',"openai/gpt-4o-mini"),api_key=os.getenv("OPENAI_API_KEY") , max_tokens=None)
dspy.configure(lm=lm)

class Job_Scan(dspy.Signature):
    """Scan the job description and resume match 1-100 and provide a reason."""
    resumes = dspy.InputField()
    job_descriptions = dspy.InputField()
    score = dspy.OutputField(desc="Score of the job description and resume match 1-100")
    reason = dspy.OutputField(desc="Reason of the score")
    name = dspy.OutputField(desc="Name of the candidate")
    email = dspy.OutputField(desc="Email of the candidate")
    phone = dspy.OutputField(desc="Phone of the candidate")
    
class Job_Scan_CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.progress = dspy.ChainOfThought(Job_Scan)
        
    def run(self, resumes, job_descriptions):
        resumes = self.ocr_pdf(resumes)
        return self.progress(resumes=resumes, job_descriptions = job_descriptions)
    
    def ocr_pdf(self,base64_pdf):
        import pytesseract
        from PIL import Image
        pdf = self.base64_to_pdf(base64_pdf)
        
        doc = fitz.open(pdf)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        if text == "":
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images(full=True)
                for image in image_list:
                    xref = image[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    text += pytesseract.image_to_string(image , lang='eng')
        return text
    def base64_to_pdf(self,base64_pdf):
        import base64
        import io
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf = io.BytesIO(pdf_bytes)
        return pdf

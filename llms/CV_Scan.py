import os
import dspy
import fitz  # PyMuPDF
import asyncio

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
        
    def forward(self, file_content, job_descriptions):
        text = self.process_pdf(file_content)
        return self.progress(resumes=text, job_descriptions=job_descriptions)
    
    def process_pdf(self, file_content):
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
            
        if not text.strip():
            # Only perform OCR if no text was extracted
            import pytesseract
            from PIL import Image
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                extracted_text = pytesseract.image_to_string(img, lang='eng')
                text += extracted_text
                
        doc.close()
        return text

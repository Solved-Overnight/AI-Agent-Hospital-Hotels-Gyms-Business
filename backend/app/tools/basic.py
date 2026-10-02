from langchain.tools import tool

# tool description is the most important part, it will be used by the agent to understand what the tool does and when to use it.
# this tool provides basic information about the dental clinic, including services offered, location, and contact details. It is designed to answer user queries related to the clinic's offerings and operational hours.

@tool
def clinic_information() -> str:
    """Return basic information about the dental clinic."""
    return (
        "Welcome to BrightSmile Dental Clinic! We provide a wide range of dental services, "
        "including routine check-ups, cleanings, fillings, crowns, and cosmetic dentistry. "
        "Our team of experienced dentists and hygienists is dedicated to ensuring your oral health "
        "and providing a comfortable experience. We are located at 123 Main Street, Anytown, USA. "
        "Our office hours are Monday to Friday from 9:00 AM to 8:00 PM. For appointments or inquiries, "
        "please call us at (555) 123-4567 or visit our website at www.dentalclinic.com."
    )
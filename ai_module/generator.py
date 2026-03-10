import os
from openai import OpenAI

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")


def get_openai_client():
    return OpenAI(
        api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
        base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
    )


def generate_job_article(job):
    try:
        client = get_openai_client()

        prompt = f"""Write a detailed SEO-optimized job article in HTML format for the following government job posting. 
Include these sections with proper HTML headings (h2, h3) and structured content:

1. Introduction - Brief overview of the recruitment
2. Vacancy Details - Number of posts and categories
3. Eligibility Criteria - Qualification and age requirements
4. Application Fee - Fee details if available
5. Important Dates - Start date, last date, exam dates
6. Salary & Pay Scale - Compensation details
7. Selection Process - How candidates will be selected
8. How to Apply - Step-by-step application process
9. Important Links - Apply link and notification link

Job Details:
- Title: {job.title}
- Organization: {job.organization}
- Department: {job.department}
- Total Posts: {job.total_posts}
- Qualification: {job.qualification}
- Age Limit: {job.age_limit}
- Application Fee: {job.application_fee}
- Salary: {job.salary}
- Start Date: {job.start_date}
- Last Date: {job.last_date}
- Apply Link: {job.apply_link}
- Selection Process: {job.selection_process}
- State: {job.state}

Write in professional, informative tone. Use proper HTML tags for formatting.
Do NOT include html, head, or body tags - just the article content with headings and paragraphs.
Make the content detailed and helpful for job seekers."""

        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are a professional content writer specializing in government job notifications and recruitment articles for Indian job seekers. Write clear, detailed, and SEO-optimized content."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4096
        )

        content = response.choices[0].message.content
        return content if content else None

    except Exception as e:
        print(f"AI content generation error: {e}")
        return generate_fallback_article(job)


def generate_fallback_article(job):
    return f"""
<h2>About {job.title}</h2>
<p>{job.organization} has released an official notification for {job.title}. 
Interested and eligible candidates can apply for this recruitment through the official website.</p>

<h2>Vacancy Details</h2>
<p><strong>Total Posts:</strong> {job.total_posts or 'As per notification'}</p>
<p><strong>Organization:</strong> {job.organization}</p>
<p><strong>Department:</strong> {job.department or 'See notification'}</p>

<h2>Eligibility Criteria</h2>
<h3>Educational Qualification</h3>
<p>{job.qualification or 'As per official notification. Please check the official notification for detailed eligibility criteria.'}</p>

<h3>Age Limit</h3>
<p>{job.age_limit or 'As per government rules. Age relaxation applicable as per norms.'}</p>

<h2>Application Fee</h2>
<p>{job.application_fee or 'Please refer to the official notification for fee details.'}</p>

<h2>Important Dates</h2>
<table class="table table-bordered">
<tr><td><strong>Start Date</strong></td><td>{job.start_date or 'Check notification'}</td></tr>
<tr><td><strong>Last Date</strong></td><td>{job.last_date or 'Check notification'}</td></tr>
</table>

<h2>Salary</h2>
<p>{job.salary or 'As per government pay scale norms.'}</p>

<h2>Selection Process</h2>
<p>{job.selection_process or 'The selection will be based on Written Exam / Interview / Merit as per the norms of the organization.'}</p>

<h2>How to Apply</h2>
<ol>
<li>Visit the official website</li>
<li>Look for the recruitment notification</li>
<li>Read the notification carefully</li>
<li>Fill the application form with correct details</li>
<li>Upload required documents</li>
<li>Pay the application fee (if applicable)</li>
<li>Submit the form and take a printout</li>
</ol>

<h2>Important Links</h2>
<p><strong>Apply Online:</strong> <a href="{job.apply_link}" target="_blank" rel="noopener">Click Here</a></p>
<p><strong>Official Notification:</strong> <a href="{job.notification_link}" target="_blank" rel="noopener">Click Here</a></p>
<p><strong>Official Website:</strong> <a href="{job.official_website}" target="_blank" rel="noopener">{job.official_website or 'Visit Official Website'}</a></p>
"""


PS C:\Users\wilso\Downloads\Househunting> $readmeContent = @"
>> # Househunting & Property Listing Platform (Kenya)
>>
>> A full-stack Django web application connecting customers seeking vacant houses and rooms with verified house owners and real estate agents in Kenya.
>>
>> ## Local Setup & Installation
>>
>> ### 1. Clone the Repository
>> \`\`\`bash
>> git clone https://github.com/vohtieno/Househunting.git
>> cd Househunting
>> \`\`\`
>>
>> ### 2. Create & Activate Virtual Environment
>> - **Windows (PowerShell):**
>> \`\`\`powershell
>> python -m venv venv
>> .\venv\Scripts\Activate
>> \`\`\`
>> - **Kali Linux / macOS:**
>> \`\`\`bash
>> python3 -m venv venv
>> source venv/bin/activate
>> \`\`\`
>>
>> ### 3. Install Dependencies
>> \`\`\`bash
>> pip install -r requirements.txt
>> \`\`\`
>>
>> ### 4. Run Migrations & Start Server
>> \`\`\`bash
>> python manage.py migrate
>> python manage.py runserver
>> \`\`\`
>> "@
>> Set-Content -Path README.md -Value $readmeContent -Encoding utf8
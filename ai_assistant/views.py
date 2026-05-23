import json
import os
import re
from decimal import Decimal
from datetime import date, timedelta
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from expenses.models import Transaction, Account, Category, Budget, SavingsGoal

# Check if Gemini API is available
import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use gemini-1.5-flash which is widely compatible
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@login_required
def chat_page_view(request):
    return render(request, 'ai_assistant/chat.html')

@login_required
@require_POST
def ai_chat_api(request):
    user = request.user
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request body'}, status=400)
        
    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
    # Gather user context for the prompt
    transactions = Transaction.objects.filter(user=user).select_related('category', 'account')[:30]
    accounts = Account.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user)
    goals = SavingsGoal.objects.filter(user=user, is_completed=False)
    
    total_balance = sum(a.balance for a in accounts)
    tx_list_str = "\n".join([
        f"- {t.date}: {t.type.upper()} of {user.currency} {t.amount} in '{t.category.name}' (Desc: {t.description})"
        for t in transactions
    ])
    
    accounts_str = "\n".join([f"- {a.name}: {user.currency} {a.balance}" for a in accounts])
    budgets_str = "\n".join([
        f"- Budget for {b.category.name if b.category else 'Global'}: {user.currency} {b.amount} (From {b.start_date} to {b.end_date})"
        for b in budgets
    ])
    goals_str = "\n".join([f"- Goal '{g.name}': target {user.currency} {g.target_amount}, current {g.current_amount}" for g in goals])

    system_prompt = f"""
You are an Elite AI Financial Advisor named "Antigravity Finance AI". You help users manage their money, track expenses, suggest budgets, detect spending patterns, and provide personalized financial insights.
Be encouraging, smart, and precise. Use the user's financial details below to give contextual answers.

USER DETAILS:
- Username: {user.username}
- Preferred Currency: {user.currency}
- Monthly Income Goal: {user.currency} {user.monthly_income_goal}
- Total Net Balance: {user.currency} {total_balance}

CURRENT ACCOUNTS:
{accounts_str or 'No accounts configured.'}

ACTIVE BUDGETS:
{budgets_str or 'No budgets set.'}

SAVINGS GOALS:
{goals_str or 'No savings goals.'}

RECENT TRANSACTIONS (last 30):
{tx_list_str or 'No recent transactions recorded.'}

Formulate your response in Markdown. Keep it structured, engaging, and professional. Mention specific categories or goals if they ask about budgets, expenses, or advice.
"""

    if model:
        try:
            prompt = f"{system_prompt}\n\nUser Question: {user_message}\nAI Advisor Response:"
            response = model.generate_content(prompt)
            return JsonResponse({'reply': response.text})
        except Exception as e:
            # Fall back to rules if API fails during call
            pass

    # =====================================================================
    # MOCK/RULE-BASED AI FALLBACK ENGINE (Context-Aware)
    # =====================================================================
    reply = ""
    lower_msg = user_message.lower()
    
    if "hello" in lower_msg or "hi" in lower_msg:
        reply = f"Hello {user.username}! I am **Antigravity Finance AI**, your personalized fintech assistant. Since the Gemini API key is currently running in local fallback mode, I am analyzing your database directly. You currently have a net balance of **{user.currency} {total_balance:,.2f}** across your accounts. What financial queries can I help you with today?"
        
    elif "spend" in lower_msg or "expense" in lower_msg or "transaction" in lower_msg:
        category_spending = {}
        for t in transactions:
            if t.type == 'expense':
                category_spending[t.category.name] = category_spending.get(t.category.name, Decimal(0)) + t.amount
        
        if category_spending:
            breakdown = "\n".join([f"- **{cat}**: {user.currency} {amt:,.2f}" for cat, amt in category_spending.items()])
            reply = f"Here is a summary of your recent expense patterns based on your last 30 transactions:\n\n{breakdown}\n\n**Suggestions**:\n- Consider setting a strict budget for your highest spending categories.\n- Keep track of your small recurring expenses, as they add up quickly!"
        else:
            reply = "You don't have any recent expense transactions logged. Go to the **Transactions** ledger page to add some, and I'll analyze them for you!"
            
    elif "budget" in lower_msg:
        if budgets.exists():
            active_budgets = "\n".join([f"- **{b.category.name if b.category else 'Global'}**: {user.currency} {b.amount:,.2f}" for b in budgets])
            reply = f"You currently have these active budgets configured:\n\n{active_budgets}\n\nTo optimize your budget, aim to save at least 20% of your monthly income goal of **{user.currency} {user.monthly_income_goal:,.2f}**."
        else:
            reply = f"You don't have any budgets set up yet. Set a budget in the **Budgets & Savings** page! A good starting budget rule is **50/30/20** (50% Needs, 30% Wants, 20% Savings)."
            
    elif "goal" in lower_msg or "save" in lower_msg:
        if goals.exists():
            active_goals = "\n".join([f"- **{g.name}**: Saved {user.currency} {g.current_amount:,.2f} of {user.currency} {g.target_amount:,.2f}" for g in goals])
            reply = f"Here are your active savings goals:\n\n{active_goals}\n\nKeep logging transactions to complete them! Every little bit counts."
        else:
            reply = "You don't have any active savings goals. Create a savings goal in the **Budgets & Savings** planner to track your progress towards buying a car, house, or building an emergency fund!"
            
    else:
        reply = f"Thank you for asking! I'm operating in context-aware fallback mode. Your total balance is **{user.currency} {total_balance:,.2f}**. You have {accounts.count()} accounts and {transactions.count()} transactions logged. To enable full generative AI chat features, make sure to add your `GEMINI_API_KEY` in the `.env` settings file!"

    return JsonResponse({'reply': reply})

@login_required
@require_POST
def parse_voice_api(request):
    user = request.user
    try:
        body = json.loads(request.body)
        voice_text = body.get('text', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request body'}, status=400)
        
    if not voice_text:
        return JsonResponse({'error': 'No text provided'}, status=400)
        
    # We will try to parse with Gemini JSON Mode. If not available, we use local parsing
    prompt = f"""
You are a transaction details parser. Look at the spoken text and extract details as JSON.
Spoken Text: "{voice_text}"

Extract:
1. "amount": Float (e.g. 15.50)
2. "type": String ('expense' or 'income')
3. "category_guess": String (one of: 'Food & Dining', 'Rent & Housing', 'Transport & Travel', 'Shopping & Fashion', 'Entertainment & Leisure', 'Utilities & Bills', 'Salary & Wage', 'Freelance & Side Hustles', 'Investments')
4. "description": String (short description of what was purchased or earned, e.g. "Pizza", "Uber ride", "Salary")
5. "date": Date string in format YYYY-MM-DD (assume today's date is {date.today().strftime('%Y-%m-%d')} unless specified otherwise)

Respond ONLY with a valid raw JSON object, no Markdown wrapping, no markdown blocks. Example:
{{"amount": 12.00, "type": "expense", "category_guess": "Food & Dining", "description": "Coffee", "date": "2026-05-23"}}
"""

    parsed_data = None
    if model:
        try:
            # Request Gemini response
            response = model.generate_content(prompt)
            # Remove any markdown wrapping if Gemini returns it
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            parsed_data = json.loads(clean_text)
        except Exception:
            parsed_data = None
            
    if not parsed_data:
        # =====================================================================
        # LOCAL REGEX & KEYWORD PARSING ENGINE (Fallback)
        # =====================================================================
        parsed_data = {
            'amount': 0.00,
            'type': 'expense',
            'category_guess': 'Food & Dining',
            'description': voice_text,
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        # 1. Parse Amount (look for numbers, "dollars", "bucks", "rupees", etc.)
        amount_match = re.search(r'(?:spent|earned|for|of)?\s*(\d+(?:\.\d{2})?)\s*(?:dollars|bucks|rupees|usd|inr|euros|pounds)?', voice_text, re.IGNORECASE)
        if amount_match:
            parsed_data['amount'] = float(amount_match.group(1))
        else:
            # Fallback check for raw number
            num_match = re.search(r'\b\d+(?:\.\d{2})?\b', voice_text)
            if num_match:
                parsed_data['amount'] = float(num_match.group(0))
                
        # 2. Parse Type
        if any(w in voice_text.lower() for w in ['earn', 'salary', 'income', 'received', 'got', 'wage', 'paycheck']):
            parsed_data['type'] = 'income'
            parsed_data['category_guess'] = 'Salary & Wage'
            
        # 3. Category Guessing
        text_lower = voice_text.lower()
        if 'eat' in text_lower or 'food' in text_lower or 'lunch' in text_lower or 'dinner' in text_lower or 'pizza' in text_lower or 'coffee' in text_lower or 'restaurant' in text_lower or 'cafe' in text_lower:
            parsed_data['category_guess'] = 'Food & Dining'
        elif 'rent' in text_lower or 'flat' in text_lower or 'house' in text_lower or 'apartment' in text_lower or 'home' in text_lower:
            parsed_data['category_guess'] = 'Rent & Housing'
        elif 'cab' in text_lower or 'taxi' in text_lower or 'uber' in text_lower or 'bus' in text_lower or 'train' in text_lower or 'flight' in text_lower or 'petrol' in text_lower or 'fuel' in text_lower or 'travel' in text_lower:
            parsed_data['category_guess'] = 'Transport & Travel'
        elif 'shop' in text_lower or 'cloth' in text_lower or 'buy' in text_lower or 'shoes' in text_lower or 'amazon' in text_lower:
            parsed_data['category_guess'] = 'Shopping & Fashion'
        elif 'movie' in text_lower or 'netflix' in text_lower or 'game' in text_lower or 'ticket' in text_lower or 'party' in text_lower or 'beer' in text_lower:
            parsed_data['category_guess'] = 'Entertainment & Leisure'
        elif 'bill' in text_lower or 'electric' in text_lower or 'water' in text_lower or 'phone' in text_lower or 'internet' in text_lower or 'wifi' in text_lower or 'gas' in text_lower:
            parsed_data['category_guess'] = 'Utilities & Bills'

        # 4. Description Cleaning
        # Remove common command verbs
        clean_desc = re.sub(r'\b(spent|spent|earned|log|add|record|dollars|bucks|rupees|usd|inr|for|on)\b', '', voice_text, flags=re.IGNORECASE)
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        parsed_data['description'] = clean_desc.capitalize() or voice_text
        
    # Map category string to category ID from database
    cat_match = Category.objects.filter(user=user, name__icontains=parsed_data['category_guess']).first()
    if not cat_match:
        # Check global system categories
        cat_match = Category.objects.filter(user__isnull=True, name__icontains=parsed_data['category_guess']).first()
        
    parsed_data['category_id'] = cat_match.id if cat_match else None
    
    return JsonResponse(parsed_data)

@login_required
def ai_insights_api(request):
    user = request.user
    
    # Calculate some analytics properties
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    transactions = Transaction.objects.filter(user=user)
    monthly_expenses = transactions.filter(type='expense', date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or Decimal(0.00)
    monthly_income = transactions.filter(type='income', date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or Decimal(0.00)
    
    # Financial health score calculation (simple dynamic rule-based index out of 100)
    health_score = 75 # Default standard base score
    
    if monthly_income > 0:
        expense_ratio = (monthly_expenses / monthly_income) * 100
        if expense_ratio > 90:
            health_score -= 30
        elif expense_ratio > 70:
            health_score -= 15
        elif expense_ratio < 50:
            health_score += 15
    else:
        if monthly_expenses > 0:
            health_score -= 25
            
    # Cap health score between 0 and 100
    health_score = max(min(health_score, 100), 10)
    
    # Find top spending category
    categories_sum = transactions.filter(type='expense', date__gte=start_of_month).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    top_cat = categories_sum[0]['category__name'] if categories_sum.exists() else "None"
    top_cat_amount = categories_sum[0]['total'] if categories_sum.exists() else Decimal(0.00)
    
    # Build recommendations list
    suggestions = []
    
    if health_score < 60:
        suggestions.append(f"Your expense ratio is high this month. Try setting strict spending limits on your top expense category: **{top_cat}**.")
    else:
        suggestions.append("You are maintaining a healthy savings margin. Keep it up! Consider routing surplus funds to your active savings goals.")
        
    if top_cat != "None" and top_cat_amount > (monthly_income * Decimal(0.3) if monthly_income > 0 else Decimal(1000)):
        suggestions.append(f"Overspending alert: You spent **{user.currency} {top_cat_amount:,.2f}** on **{top_cat}**, which represents a significant chunk of your funds.")
        
    # AI Predictions for next month
    pred_expense = monthly_expenses * Decimal(1.05) if monthly_expenses > 0 else Decimal(250.00)
    
    return JsonResponse({
        'health_score': health_score,
        'monthly_expenses': float(monthly_expenses),
        'monthly_income': float(monthly_income),
        'top_category': top_cat,
        'top_category_spent': float(top_cat_amount),
        'predicted_next_month_expenses': float(round(pred_expense, 2)),
        'suggestions': suggestions
    })

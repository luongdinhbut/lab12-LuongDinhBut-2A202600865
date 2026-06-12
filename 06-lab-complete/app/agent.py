import os
import google.generativeai as genai

# ─────────────────────────────────────────────────────────
# Các Tools của Agent
# ─────────────────────────────────────────────────────────
def get_weather(location: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một thành phố/địa điểm.
    
    Args:
        location: Tên thành phố hoặc địa điểm
    """
    return f"Thời tiết tại {location} hiện tại là 28 độ C, trời nắng đẹp."

def get_crypto_price(coin: str) -> str:
    """Lấy giá trị của một đồng tiền điện tử (crypto).
    
    Args:
        coin: Mã đồng tiền (vd: BTC, ETH)
    """
    prices = {"BTC": "$65,000", "ETH": "$3,500"}
    return prices.get(coin.upper(), f"Không tìm thấy giá cho {coin}")

# ─────────────────────────────────────────────────────────
# Agent Logic
# ─────────────────────────────────────────────────────────
def ask(question: str) -> str:
    """
    Hàm giao tiếp với Agent. Agent có khả năng gọi Tools tự động bằng Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_key_here":
        return "⚠️ Cảnh báo: Cần thiết lập GEMINI_API_KEY hợp lệ trong file `.env.local` để sử dụng Agent này."

    genai.configure(api_key=api_key)
    
    # Khởi tạo mô hình kèm tools và system instruction
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        tools=[get_weather, get_crypto_price],
        system_instruction="Bạn là một AI Agent thông minh. Bạn hãy luôn sử dụng tools nếu người dùng hỏi về thời tiết hoặc giá crypto."
    )

    try:
        # Bắt đầu phiên chat (cho phép model tự động gọi tool và trả về kết quả cuối cùng)
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(question)
        return response.text
        
    except Exception as e:
        return f"Lỗi gọi Gemini API: {str(e)}"

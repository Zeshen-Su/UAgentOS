import httpx
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Get the current weather for a given city using OpenWeatherMap.请在下方填入您的API Key。
    """
    
    api_key = "" 
    url = f""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            # print(f"OpenWeatherMap Response Status: {response.status_code}")
            
            if response.status_code == 404:
                return f"未找到城市 '{city}'，请检查拼写。"
            response.raise_for_status()
            data = response.json()
            
            city_name = data.get("name", city)
            temp = data.get("main", {}).get("temp", "N/A")
            weather_desc = "N/A"
            if data.get("weather"):
                weather_desc = data["weather"][0].get("description", "N/A")
            
            return (
                f"城市: {city_name}\n"
                f"天气: {weather_desc}\n"
                f"温度: {temp}°C"
            )
    except httpx.HTTPStatusError as e:
        return f"API 请求失败，状态码: {e.response.status_code}"
    except Exception as e:
        return f"获取天气时发生错误: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')

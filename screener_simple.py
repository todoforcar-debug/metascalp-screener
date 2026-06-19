import asyncio
import json
import urllib.request
import urllib.error
from urllib.parse import urlencode

class MetaScalpClient:
    """Простой клиент для MetaScalp API без зависимостей"""
    
    def __init__(self, host='127.0.0.1', port=None):
        self.host = host
        self.port = port
        self.base_url = None
        
    async def discover(self):
        """Автоматически находит работающий MetaScalp"""
        for port in range(17845, 17856):
            try:
                url = f'http://{self.host}:{port}/ping'
                response = urllib.request.urlopen(url, timeout=1)
                self.base_url = f'http://{self.host}:{port}'
                print(f"✅ Найден MetaScalp на {self.base_url}\n")
                return self
            except (urllib.error.URLError, urllib.error.HTTPError):
                continue
        
        raise Exception(f"❌ MetaScalp не найден на портах 17845-17855")
    
    def _request(self, method, endpoint, params=None):
        """Делает HTTP запрос"""
        url = f"{self.base_url}{endpoint}"
        
        if params and method == 'GET':
            url += '?' + urlencode(params)
        
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None
    
    async def get_connections(self):
        """Получает список подключённых бирж"""
        return self._request('GET', '/api/connections')
    
    async def get_tickers(self, connection_id):
        """Получает список монет для биржи"""
        return self._request('GET', f'/api/connections/{connection_id}/tickers')


async def main():
    print("🚀 MetaScalp Screener (Облегчённая версия)\n")
    
    try:
        # Подключаемся
        print("📡 Подключение к MetaScalp...")
        client = MetaScalpClient()
        await client.discover()
        
        # Получаем биржи
        print("📊 Загрузка бирж...\n")
        connections_data = await client.get_connections()
        
        if not connections_data or not connections_data.get('connections'):
            print("❌ Нет подключённых бирж!")
            print("⚠️  Убедись что:")
            print("   1. MetaScalp запущен на твоём ПК")
            print("   2. Добавлена хотя бы одна биржа в MetaScalp")
            return
        
        connections = connections_data['connections']
        
        # Показываем меню бирж
        print("=== ДОСТУПНЫЕ БИРЖИ ===")
        for i, conn in enumerate(connections, 1):
            print(f"{i}. {conn.get('exchange', 'Unknown')}")
        
        # Выбираем биржу
        while True:
            try:
                choice = input("\n➡️  Выбери номер биржи: ")
                selected = connections[int(choice) - 1]
                break
            except (ValueError, IndexError):
                print("❌ Неверный номер! Попробуй снова.")
        
        print(f"\n📈 Загрузка монет {selected.get('exchange')}...")
        
        # Получаем монеты
        tickers_data = await client.get_tickers(selected['id'])
        
        if not tickers_data or not tickers_data.get('tickers'):
            print("❌ Не удалось загрузить монеты!")
            return
        
        tickers = tickers_data['tickers']
        
        # Сортируем по объёму
        tickers = sorted(tickers, key=lambda x: x.get('volume_24h', 0), reverse=True)
        
        # Фильтры
        print("\n⚙️  ФИЛЬТРЫ:")
        min_volume_input = input("💰 Минимальный объём (USD) [0]: ").strip() or "0"
        search_input = input("🔍 Поиск (название монеты или пусто): ").strip().upper()
        
        try:
            min_volume = float(min_volume_input)
        except ValueError:
            min_volume = 0
        
        # Фильтруем
        filtered = [
            t for t in tickers 
            if t.get('volume_24h', 0) >= min_volume
            and (not search_input or search_input in t.get('name', '').upper())
        ]
        
        # Форматирование
        def format_price(price):
            if price >= 1:
                return f"{price:.2f}"
            elif price >= 0.01:
                return f"{price:.4f}"
            else:
                return f"{price:.8f}"
        
        def format_volume(volume):
            if volume >= 1_000_000:
                return f"${volume/1_000_000:.1f}M"
            elif volume >= 1_000:
                return f"${volume/1_000:.1f}K"
            else:
                return f"${volume:.0f}"
        
        # Показываем результаты
        print("\n" + "=" * 90)
        print(f"{'МОНЕТА':<15} {'ЦЕНА':<15} {'ОБЪЁМ 24H':<20} {'ИЗМЕНЕНИЕ 24H':<15}")
        print("=" * 90)
        
        count = 0
        for ticker in filtered[:50]:  # Показываем максимум 50
            name = ticker.get('name', '?')[:12]
            price = ticker.get('last_price', 0)
            volume = ticker.get('volume_24h', 0)
            change = ticker.get('price_change_24h', 0)
            
            vol_str = format_volume(volume)
            change_str = f"{change:+.2f}%"
            
            print(f"{name:<15} ${format_price(price):<14} {vol_str:<20} {change_str:<15}")
            count += 1
        
        print("=" * 90)
        print(f"✅ Показано {count} монет из {len(filtered)} найденных\n")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n⚠️  Убедись что:")
        print("   1. MetaScalp запущен на твоём ПК")
        print("   2. Добавлена хотя бы одна биржа")
        print("   3. Работает подключение к интернету")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from metascalp import MetaScalpClient

async def main():
    print("🚀 MetaScalp Screener\n")
    
    try:
        # Подключаемся
        print("📡 Подключение к MetaScalp...")
        client = await MetaScalpClient.discover()
        
        # Получаем биржи
        print("📊 Загрузка бирж...\n")
        connections = await client.get_connections()
        
        if not connections['connections']:
            print("❌ Нет подключённых бирж!")
            return
        
        # Показываем меню бирж
        print("=== ДОСТУПНЫЕ БИРЖИ ===")
        for i, conn in enumerate(connections['connections'], 1):
            print(f"{i}. {conn['exchange']}")
        
        # Выбираем биржу
        choice = input("\n➡️  Выбери номер биржи: ")
        selected = connections['connections'][int(choice) - 1]
        
        print(f"\n📈 Загрузка монет {selected['exchange']}...")
        
        # Получаем монеты
        response = await client.get_tickers(selected['id'])
        tickers = response.get('tickers', [])
        
        # Сортируем по объёму
        tickers = sorted(tickers, key=lambda x: x.get('volume_24h', 0), reverse=True)
        
        # Фильтр
        print("\n⚙️  ФИЛЬТРЫ:")
        min_volume = input("💰 Минимальный объём (USD) [0]: ").strip() or "0"
        search = input("🔍 Поиск (название монеты или пусто): ").strip().upper()
        
        # Фильтруем
        filtered = [t for t in tickers 
                   if t.get('volume_24h', 0) >= float(min_volume)
                   and (not search or search in t.get('name', '').upper())]
        
        # Показываем
        print("\n" + "=" * 90)
        print(f"{'МОНЕТА':<15} {'ЦЕНА':<15} {'ОБЪЁМ 24H':<20} {'ИЗМЕНЕНИЕ 24H':<15}")
        print("=" * 90)
        
        for ticker in filtered[:30]:
            name = ticker.get('name', '?')[:12]
            price = ticker.get('last_price', 0)
            volume = ticker.get('volume_24h', 0)
            change = ticker.get('price_change_24h', 0)
            
            # Форматируем объём
            if volume >= 1_000_000:
                vol_str = f"${volume/1_000_000:.1f}M"
            elif volume >= 1_000:
                vol_str = f"${volume/1_000:.1f}K"
            else:
                vol_str = f"${volume:.0f}"
            
            # Форматируем изменение
            change_str = f"{change:+.2f}%"
            
            print(f"{name:<15} ${price:<14.2f} {vol_str:<20} {change_str:<15}")
        
        print("=" * 90)
        print(f"✅ Показано {len(filtered)} монет из {len(tickers)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("⚠️  Убедись что MetaScalp запущен на порте 17845-17855!")

if __name__ == "__main__":
    asyncio.run(main())
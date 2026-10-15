using System;
using HomederMatchService;

class Program
{
    static async Task Main()
    {
        Console.WriteLine("🏠 HOMEDER - MATCH SERVICE (через API)");

        var baseUrl = "http://localhost:8000/api/v1";
        var apiKey = Environment.GetEnvironmentVariable("MATCH_API_KEY") ?? "";

        var matchService = new MatchService(baseUrl, apiKey);

        Console.WriteLine("\n🔄 Тестируем запись метча через API...");
        bool result = await matchService.RecordMatchAsync(swiperId: 1, propertyId: 2);

        if (result)
        {
            Console.WriteLine("УСПЕХ! Метч записан через REST API");
        }
        else
        {
            Console.WriteLine("ОШИБКА! Не удалось записать метч");
        }

        Console.WriteLine("\nТест завершён!");
        Console.ReadLine();
    }
}
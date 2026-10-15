using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace HomederMatchService
{
    public class MatchService
    {
        private readonly HttpClient _httpClient;

        public MatchService(string baseUrl, string apiKey)
        {
            _httpClient = new HttpClient { BaseAddress = new Uri(baseUrl) };
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
        }

        public async Task<bool> RecordMatchAsync(long swiperId, long propertyId)
        {
            try
            {
                var payload = new { user_id = swiperId, prop_id = propertyId };
                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/favorites/", content);

                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Метч записан через API");
                    return true;
                }

                Console.WriteLine($"Ошибка API: {response.StatusCode}");
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
                return false;
            }
        }
    }
}
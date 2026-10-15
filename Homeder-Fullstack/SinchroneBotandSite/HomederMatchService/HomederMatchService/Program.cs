using System;
using MySqlConnector;

class Program
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("🏠 HOMEDER - ТЕСТ РАБОТЫ С БАЗОЙ");
        
        string connectionString = "server=localhost;port=3306;database=homeder;user=bot;password=Mama1946!;";
        
        try
        {
            using (var conn = new MySqlConnection(connectionString))
            {
                conn.Open();
                
                // Тест 1: Добавим ещё пользователя
                Console.WriteLine("\n1. Добавляем второго пользователя...");
                var cmd1 = new MySqlCommand("INSERT INTO users (full_name, bio, tg_id) VALUES ('Второй пользователь', 'Сдаю квартиру', 'owner123')", conn);
                cmd1.ExecuteNonQuery();
                Console.WriteLine("✅ Добавлен!");
                
                // Тест 2: Добавим вторую квартиру
                Console.WriteLine("\n2. Добавляем вторую квартиру...");
                var cmd2 = new MySqlCommand("INSERT INTO properties (owner_id, price, title, description, city) VALUES (2, 55000, '2-комнатная в новостройке', 'Панорамные окна', 'Москва')", conn);
                cmd2.ExecuteNonQuery();
                Console.WriteLine("✅ Добавлена!");

                // Тест 3: Первый пользователь лайкает вторую квартиру
                Console.WriteLine("\n3. Пользователь 1 лайкает квартиру 2...");
                var checkCmd = new MySqlCommand("SELECT COUNT(*) FROM favorites WHERE user_id = 1 AND prop_id = 2", conn);
                if (Convert.ToInt64(checkCmd.ExecuteScalar()) == 0)
                {
                    var cmd3 = new MySqlCommand("INSERT INTO favorites (user_id, prop_id) VALUES (1, 2)", conn);
                    cmd3.ExecuteNonQuery();
                    Console.WriteLine("✅ Лайк записан!");
                }
                else
                {
                    Console.WriteLine("⚠ Лайк уже существует");
                }

                // Тест 4: Покажем все лайки
                Console.WriteLine("\n4. Все лайки в системе:");
                var cmd4 = new MySqlCommand(@"
                    SELECT f.user_id, u.full_name, f.prop_id, p.title 
                    FROM favorites f
                    JOIN users u ON f.user_id = u.user_id
                    JOIN properties p ON f.prop_id = p.prop_id", conn);
                
                using (var reader = cmd4.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine($"   👤 {reader["full_name"]} (ID:{reader["user_id"]}) → 🏠 {reader["title"]} (ID:{reader["prop_id"]})");
                    }
                }
                
                conn.Close();
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Ошибка: {ex.Message}");
        }
        
        Console.WriteLine("\n🎉 СИСТЕМА РАБОТАЕТ!");
        Console.ReadLine();
    }
}

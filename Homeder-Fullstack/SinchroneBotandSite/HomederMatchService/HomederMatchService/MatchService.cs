using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


using System;
using MySqlConnector;

namespace HomederMatchService
{
    public class MatchService
    {
        // Строка подключения к вашей базе данных
        private string connectionString = "server=localhost;port=3306;database=homeder;user=bot;password=Mama1946!;";

        /// <summary>
        /// ЗАПИСЬ МЕТЧА ПРИ СВАЙПЕ ВПРАВО
        /// </summary>
        public bool RecordMatch(long swiperId, long propertyId)
        {
            try
            {
                Console.WriteLine($"🔄 Пытаюсь записать метч: Пользователь {swiperId} лайкнул квартиру {propertyId}");

                using (var connection = new MySqlConnection(connectionString))
                {
                    connection.Open();
                    Console.WriteLine("✅ Подключение к базе данных установлено");

                    // 1. Проверяем, существует ли квартира
                    if (!PropertyExists(propertyId, connection))
                    {
                        Console.WriteLine($"❌ Квартира с ID {propertyId} не найдена!");
                        return false;
                    }

                    // 2. Проверяем, существует ли пользователь
                    if (!UserExists(swiperId, connection))
                    {
                        Console.WriteLine($"❌ Пользователь с ID {swiperId} не найден!");
                        return false;
                    }

                    // 3. Проверяем, не лайкал ли уже
                    if (IsFavoriteExists(swiperId, propertyId, connection))
                    {
                        Console.WriteLine($"⚠️ Пользователь уже лайкнул эту квартиру");
                        return true;
                    }

                    // 4. ЗАПИСЫВАЕМ В ТАБЛИЦУ favorites (правильная таблица!)
                    string insertQuery = @"
                        INSERT INTO favorites (user_id, prop_id) 
                        VALUES (@userId, @propertyId)";

                    using (var command = new MySqlCommand(insertQuery, connection))
                    {
                        command.Parameters.AddWithValue("@userId", swiperId);
                        command.Parameters.AddWithValue("@propertyId", propertyId);

                        int rowsAffected = command.ExecuteNonQuery();

                        if (rowsAffected > 0)
                        {
                            Console.WriteLine($"✅ МЕТЧ УСПЕШНО ЗАПИСАН В favorites!");
                            Console.WriteLine($"   👤 Пользователь: {swiperId}");
                            Console.WriteLine($"   🏠 Квартира: {propertyId}");

                            // Получаем владельца для уведомления
                            long ownerId = GetPropertyOwnerId(propertyId, connection);
                            if (ownerId > 0)
                            {
                                Console.WriteLine($"   👑 Владелец квартиры: {ownerId}");

                                // Проверяем взаимный лайк
                                CheckMutualLike(ownerId, swiperId, propertyId, connection);
                            }

                            return true;
                        }
                        else
                        {
                            Console.WriteLine("❌ Ни одна запись не добавлена");
                            return false;
                        }
                    }
                }
            }
            catch (MySqlException ex)
            {
                Console.WriteLine($"❌ ОШИБКА MySQL: {ex.Message}");
                Console.WriteLine($"Код ошибки: {ex.Number}");
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ ОШИБКА: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Проверяет существование квартиры
        /// </summary>
        private bool PropertyExists(long propertyId, MySqlConnection connection)
        {
            string query = "SELECT COUNT(*) FROM properties WHERE prop_id = @propertyId";

            using (var command = new MySqlCommand(query, connection))
            {
                command.Parameters.AddWithValue("@propertyId", propertyId);
                long count = Convert.ToInt64(command.ExecuteScalar());
                return count > 0;
            }
        }

        /// <summary>
        /// Проверяет существование пользователя
        /// </summary>
        private bool UserExists(long userId, MySqlConnection connection)
        {
            string query = "SELECT COUNT(*) FROM users WHERE user_id = @userId";

            using (var command = new MySqlCommand(query, connection))
            {
                command.Parameters.AddWithValue("@userId", userId);
                long count = Convert.ToInt64(command.ExecuteScalar());
                return count > 0;
            }
        }

        /// <summary>
        /// Проверяет, лайкал ли уже пользователь эту квартиру
        /// </summary>
        private bool IsFavoriteExists(long userId, long propertyId, MySqlConnection connection)
        {
            string query = "SELECT COUNT(*) FROM favorites WHERE user_id = @userId AND prop_id = @propertyId";

            using (var command = new MySqlCommand(query, connection))
            {
                command.Parameters.AddWithValue("@userId", userId);
                command.Parameters.AddWithValue("@propertyId", propertyId);
                long count = Convert.ToInt64(command.ExecuteScalar());
                return count > 0;
            }
        }

        /// <summary>
        /// Получает ID владельца квартиры
        /// </summary>
        private long GetPropertyOwnerId(long propertyId, MySqlConnection connection)
        {
            string query = "SELECT owner_id FROM properties WHERE prop_id = @propertyId";

            using (var command = new MySqlCommand(query, connection))
            {
                command.Parameters.AddWithValue("@propertyId", propertyId);
                var result = command.ExecuteScalar();
                return result != null && result != DBNull.Value ? Convert.ToInt64(result) : 0;
            }
        }

        /// <summary>
        /// Проверяет взаимный лайк
        /// </summary>
        private void CheckMutualLike(long ownerId, long swiperId, long propertyId, MySqlConnection connection)
        {
            // Ищем, лайкал ли владелец квартиры этого пользователя
            string query = @"
                SELECT COUNT(*) FROM favorites f
                JOIN properties p ON f.prop_id = p.prop_id
                WHERE f.user_id = @ownerId 
                AND p.owner_id = @swiperId";

            using (var command = new MySqlCommand(query, connection))
            {
                command.Parameters.AddWithValue("@ownerId", ownerId);
                command.Parameters.AddWithValue("@swiperId", swiperId);

                long mutualCount = Convert.ToInt64(command.ExecuteScalar());

                if (mutualCount > 0)
                {
                    Console.WriteLine("🎉 ВЗАИМНЫЙ ЛАЙК! Оба пользователя лайкнули друг друга!");
                    SendTelegramNotification(swiperId, ownerId);
                }
            }
        }

        /// <summary>
        /// Отправка уведомления в Telegram
        /// </summary>
        private void SendTelegramNotification(long user1Id, long user2Id)
        {
            Console.WriteLine($"📱 Взаимный лайк между {user1Id} и {user2Id}!");
        }

        /// <summary>
        /// Получает все лайки пользователя
        /// </summary>
        public void GetUserMatches(long userId)
        {
            try
            {
                using (var connection = new MySqlConnection(connectionString))
                {
                    connection.Open();

                    string query = @"
                        SELECT f.user_id, f.prop_id, 
                               u.full_name as user_name,
                               p.title as property_title,
                               p.owner_id
                        FROM favorites f
                        JOIN users u ON f.user_id = u.user_id
                        JOIN properties p ON f.prop_id = p.prop_id
                        WHERE f.user_id = @userId";

                    using (var command = new MySqlCommand(query, connection))
                    {
                        command.Parameters.AddWithValue("@userId", userId);

                        using (var reader = command.ExecuteReader())
                        {
                            Console.WriteLine($"\n📋 ЛАЙКИ ПОЛЬЗОВАТЕЛЯ {userId}:");
                            Console.WriteLine("----------------------------------------");

                            int count = 0;
                            while (reader.Read())
                            {
                                count++;
                                long propId = reader.GetInt64("prop_id");
                                string userName = reader.GetString("user_name");
                                string propTitle = reader.GetString("property_title");
                                long ownerId = reader.GetInt64("owner_id");

                                Console.WriteLine($"{count}. {userName} лайкнул: \"{propTitle}\" (ID: {propId})");
                                Console.WriteLine($"   Владелец квартиры: {ownerId}");
                            }

                            if (count == 0)
                            {
                                Console.WriteLine("Лайков не найдено");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка при получении лайков: {ex.Message}");
            }
        }
    }
}

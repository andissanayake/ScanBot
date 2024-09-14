using Microsoft.Extensions.Configuration;
using RabbitMQ.Client;
using System.Text;

namespace Service.Messages
{
    public interface IMessageQueueService
    {
        void SendMessage(string message);
    }

    public class RabbitMQService : IMessageQueueService
    {
        private readonly ConnectionFactory _factory;
        private readonly string _queueName;

        public RabbitMQService(IConfiguration configuration)
        {
            _factory = new ConnectionFactory
            {
                HostName = configuration["RabbitMQ:HostName"],
                UserName = configuration["RabbitMQ:UserName"],
                Password = configuration["RabbitMQ:Password"]
            };
            _queueName = configuration["RabbitMQ:QueueName"];
        }

        public void SendMessage(string message)
        {
            using var connection = _factory.CreateConnection();
            using var channel = connection.CreateModel();

            channel.QueueDeclare(queue: _queueName,
                                 durable: false,
                                 exclusive: false,
                                 autoDelete: false,
                                 arguments: null);

            var body = Encoding.UTF8.GetBytes(message);

            channel.BasicPublish(exchange: "",
                                 routingKey: _queueName,
                                 basicProperties: null,
                                 body: body);
        }
    }
}

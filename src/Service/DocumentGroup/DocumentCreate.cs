using Data;
using System.Text.Json;

namespace Service.DocumentGroup
{
    public class DocumentCreateRequest
    {
        public int Id { get; set; }
        public string FileName { get; set; }
        public string ContentType { get; set; }
        public string FilePath { get; set; }
        public string OwnerId { get; set; }
        public DateTime UploadedDate { get; set; }
        public string FileKey { get; set; }
    }
    public partial class DocumentService
    {
        public async Task<AppResponse<bool>> DocumentCreate(DocumentCreateRequest doc)
        {
            var ndoc = new Document { FileName = doc.FileName, ContentType = doc.ContentType, FilePath = doc.FilePath, OwnerId = doc.OwnerId, UploadedDate = DateTime.UtcNow, Status = "UPLOADED", FileKey = doc.FileKey };
            await _context.Documents.AddAsync(ndoc);
            await _context.SaveChangesAsync();
            messageQueueService.SendMessage(JsonSerializer.Serialize(ndoc));
            return AppResponse<bool>.SuccessResponse(true);
        }

    }
}

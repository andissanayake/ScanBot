using Data;
using Microsoft.EntityFrameworkCore;
using Service.Messages;
using System.Text.Json;

namespace Service.DocumentGroup
{
    public class DocumentListLitem
    {
        public int Id { get; set; }
        public string FileName { get; set; }
        public string ContentType { get; set; }
        public string FilePath { get; set; }
        public string OwnerId { get; set; }
        public string Status { get; set; }
        public DateTime UploadedDate { get; set; }
        public string Segments { get; set; }
    }
    public class DocumentListResponse
    {
        public List<DocumentListLitem> Documents { get; set; }
    }
    public partial class DocumentService(
        ApplicationDbContext applicationDbContext, IMessageQueueService messageQueueService)
    {
        private readonly ApplicationDbContext _context = applicationDbContext;
        public async Task<AppResponse<DocumentListResponse>> DocumentListAsync(string userId)
        {
            var docs = await _context.Documents
                    .Where(d => d.OwnerId == userId)
                    .Select(d => new DocumentListLitem() { FileName = d.FileName, OwnerId = d.OwnerId, FilePath = d.FilePath, Id = d.Id, UploadedDate = d.UploadedDate, ContentType = d.ContentType, Status = d.Status })
                    .ToListAsync();
            foreach (var doc in docs)
            {
                var segments = _context.DocumentSegments.Where(d => d.DocumentId == doc.Id).ToList(); ;
                doc.Segments = JsonSerializer.Serialize(segments);
            }
            return AppResponse<DocumentListResponse>.SuccessResponse(new DocumentListResponse() { Documents = docs });
        }

    }
}

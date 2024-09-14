using Data;

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
    }
    public partial class DocumentService
    {
        public async Task<AppResponse<bool>> DocumentCreate(DocumentCreateRequest doc)
        {
            var docs = await _context.Documents.AddAsync(new Document { FileName = doc.FileName, ContentType = doc.ContentType, FilePath = doc.FilePath, OwnerId = doc.OwnerId, UploadedDate = DateTime.UtcNow });
            await _context.SaveChangesAsync();
            return AppResponse<bool>.SuccessResponse(true);
        }

    }
}

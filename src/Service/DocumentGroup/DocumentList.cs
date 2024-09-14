using Data;
using Microsoft.EntityFrameworkCore;

namespace Service.DocumentGroup
{
    public class DocumentListLitem
    {
        public int Id { get; set; }
        public string FileName { get; set; }
        public string ContentType { get; set; }
        public string FilePath { get; set; }
        public string OwnerId { get; set; }
        public DateTime UploadedDate { get; set; }
    }
    public class DocumentListResponse
    {
        public List<DocumentListLitem> Documents { get; set; }
    }
    public partial class DocumentService(
        ApplicationDbContext applicationDbContext)
    {
        private readonly ApplicationDbContext _context = applicationDbContext;
        public async Task<AppResponse<DocumentListResponse>> DocumentListAsync(string userId)
        {
            var docs = await _context.Documents
                    .Where(d => d.OwnerId == userId)
                    .Select(d => new DocumentListLitem() { FileName = d.FileName, OwnerId = d.OwnerId, FilePath = d.FilePath, Id = d.Id, UploadedDate = d.UploadedDate, ContentType = d.ContentType })
                    .ToListAsync();
            return AppResponse<DocumentListResponse>.SuccessResponse(new DocumentListResponse() { Documents = docs });
        }

    }
}

using Microsoft.AspNetCore.Mvc;
using Service;
using Service.DocumentGroup;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DocumentsController : ControllerBase
    {
        private readonly DocumentService _documentService;
        private readonly string _webRootPath;
        public DocumentsController(DocumentService documentService, IWebHostEnvironment env)
        {
            _documentService = documentService;
            _webRootPath = env.WebRootPath;
        }

        [HttpGet]
        public async Task<AppResponse<DocumentListResponse>> GetDocuments()
        {
            var id = User.FindFirst("Id")?.Value ?? "";
            return await _documentService.DocumentListAsync(id);
        }

        [HttpPost]
        public async Task<AppResponse<bool>> PostDocument([FromForm] IFormFile file)
        {
            if (file == null || file.Length == 0)
                return AppResponse<bool>.ErrorResponse("doc", "No documents attached.");

            var filePath = Path.Combine(_webRootPath, "Documents", file.FileName);
            Directory.CreateDirectory(Path.GetDirectoryName(filePath));

            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            var document = new DocumentCreateRequest
            {
                FileName = file.FileName,
                FilePath = filePath,
                ContentType = file.ContentType,
                UploadedDate = DateTime.Now
            };

            return await _documentService.DocumentCreate(document);

        }
    }

}

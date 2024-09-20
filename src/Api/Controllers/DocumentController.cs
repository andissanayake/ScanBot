using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Service;
using Service.DocumentGroup;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]/[action]")]
    [Authorize]
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

            var fileExtension = Path.GetExtension(file.FileName); // Get the file extension
            var newFileName = Guid.NewGuid().ToString() + fileExtension; // Construct new file name with extension
            var filePath = Path.Combine(_webRootPath, "Documents", newFileName); // Combine path

            var id = User.FindFirst("Id")?.Value ?? "";
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
                UploadedDate = DateTime.Now,
                OwnerId = id,
                FileKey = newFileName,
            };

            return await _documentService.DocumentCreate(document);

        }

        [HttpGet]
        public async Task<AppResponse<DocumentSearchResponse>> DocumentSearch([FromQuery] string searchText, [FromQuery] int pageNumber = 1, [FromQuery] int pageSize = 10)
        {
            var id = User.FindFirst("Id")?.Value ?? "";
            return await _documentService.DocumentSearchAsync(new DocumentSearchRequest() { OwnerId = id, PageNumber = pageNumber, PageSize = pageSize, SearchText = searchText });
        }

    }

}

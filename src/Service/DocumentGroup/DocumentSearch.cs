using System.Net.Http.Json;

namespace Service.DocumentGroup
{
    public class DocumentSearchRequest
    {
        public string OwnerId { get; set; }
        public string SearchText { get; set; }
        public int PageNumber { get; set; } = 1;  // Default value
        public int PageSize { get; set; } = 10;   // Default value
    }
    public class DocumentSearchItem
    {
        public int Id { get; set; }
        public string FileName { get; set; }
        public string ContentType { get; set; }
        public string FilePath { get; set; }
        public string TextContent { get; set; }
        public double CosineSimilarity { get; set; }
    }
    public class DocumentSearchResponse
    {
        public List<DocumentSearchItem> Items { get; set; }
    }
    public partial class DocumentService
    {
        public async Task<AppResponse<DocumentSearchResponse>> DocumentSearchAsync(DocumentSearchRequest req)
        {
            var query = $"owner_id={req.OwnerId}&search_text={Uri.EscapeDataString(req.SearchText)}&page_number={req.PageNumber}&page_size={req.PageSize}";
            var url = $"http://document-api:8000/search?{query}";

            // Make the GET request
            var response = await _httpClient.GetFromJsonAsync<List<DocumentSearchItem>>(url);

            // Map the response to DocumentSearchResponse
            var documentSearchResponse = new DocumentSearchResponse
            {
                Items = response,
            };

            return AppResponse<DocumentSearchResponse>.SuccessResponse(documentSearchResponse);
        }
    }
}

namespace Data
{
    public class Document
    {
        public int Id { get; set; }
        public string FileKey { get; set; }
        public string FileName { get; set; }
        public string ContentType { get; set; }
        public string FilePath { get; set; }
        public string OwnerId { get; set; }
        public string Status { get; set; }
        public DateTime UploadedDate { get; set; }
    }
    public class DocumentSegment
    {
        public int Id { get; set; }
        public int DocumentId { get; set; }
        public int PageId { get; set; }
        public string TextContent { get; set; }
        public double[] Embedding { get; set; }
        public DateTime UploadedDate { get; set; }

    }
}

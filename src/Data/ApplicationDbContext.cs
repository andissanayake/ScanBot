using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace Data
{
    public class ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : IdentityDbContext<ApplicationUser>(options)
    {
        public DbSet<Document> Documents { get; set; }
        public DbSet<DocumentSegment> DocumentSegments { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<DocumentSegment>()
                .Property(e => e.Embedding)
                .HasConversion(new VectorValueConverter())
                .HasColumnType("vector(768)");  // Set the column type explicitly

            base.OnModelCreating(modelBuilder);
        }
    }
}

using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

public class VectorValueConverter : ValueConverter<double[], string>
{
    public VectorValueConverter()
        : base(
            v => string.Join(",", v),  // Convert double[] to comma-separated string
            v => v.Split(new[] { ',' })  // Use an explicit array for the separator
                  .Select(double.Parse)
                  .ToArray(),
            null)  // Explicitly pass 'null' for mapping hints
    {
    }
}

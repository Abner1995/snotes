# Log  

```bash  
Install-Package Serilog.AspNetCore -Version 9.0.0  
Install-Package Serilog.Sinks.ApplicationInsights -Version 4.0.0  
```  

1. 在Program.cs中添加以下代码：  
```csharp    
builder.Host.UseSerilog((context, configuration) =>
    configuration.ReadFrom.Configuration(context.Configuration)
    //configuration
//.MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
//.MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Information)
//.WriteTo.Console(outputTemplate: "[{Timestamp:dd-MM HH:mm:ss} {Level:u3}] |{SourceContext}| {NewLine}{Message:lj}{NewLine}{Exception}")
);

app.UseSerilogRequestLogging();
```  

2. 在appsettings.json中添加以下代码：  
```json  
"Serilog": {
  "Using": [
    "Serilog.Sinks.ApplicationInsights"
  ],
  "MinimumLevel": {
    "Override": {
      "Microsoft": "Warning",
      "Microsoft.EntityFrameworkCore": "Information"
    }
  },
  "WriteTo": [
    {
      "Name": "Console",
      "Args": {
        "outputTemplate": "[{Timestamp:dd-MM HH:mm:ss} {Level:u3}] |{SourceContext}| {NewLine}{Message:lj}{NewLine}{Exception}"
      }
    },
    {
      "Name": "File",
      "Args": {
        "path": "Logs/CleanArchitecture-Api-.log",
        "rollingInterval": "Day",
        "rollOnFileSizeLimit": true,
        "formatter": "Serilog.Formatting.Compact.CompactJsonFormatter, Serilog.Formatting.Compact"
      }
    },
    {
      "Name": "ApplicationInsights",
      "Args": {
        "telemetryConverter": "Serilog.Sinks.ApplicationInsights.TelemetryConverters.TraceTelemetryConverter, Serilog.Sinks.ApplicationInsights"
      }
    }
  ]
}
```  

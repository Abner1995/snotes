# Order

整洁架构

![alt text](../../../images/dotnet/EShopMicroservices/OrderMicroserviceDDDCQRSCleanArchitecture.png)

![alt text](../../../images/dotnet/EShopMicroservices/TacticalDDDPatternsOrderMicroservice.png)

![alt text](../../../images/dotnet/EShopMicroservices/DomainEventsOrderMicroservice.png)

![alt text](../../../images/dotnet/EShopMicroservices/DomainEventsOrderMicroservice.png)

Ordering.Application
引入
BuildingBlocks
Ordering.Domain

Ordering.Infrastructure
引入
Ordering.Application

Ordering.API
引入
Ordering.Application
Ordering.Infrastructure

```{toctree}
Ordering.Domain
Ordering.Infrastructure
```
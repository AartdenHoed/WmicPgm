using ConfigMan.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceModel;
using System.Text;
using System.Threading.Tasks;

namespace ConfigMan.Interfaces
{
    [ServiceContract]
    public interface IReadWmicFile
    {
        [OperationContract]
        WMIrapport Wmirapport(string inputfile);
        
    }
}

using ConfigMan.Interfaces;
using ConfigMan.Models;
using System.IO;

namespace ConfigMan.Helpers
{
    public class ReadWMICfile : IReadWmicFile
    {
        public WMIrapport Wmirapport(string dsname)
        {
            string line;

            if (File.Exists(dsname))
            {
                // Read the file and display it line by line.
                StreamReader file = new StreamReader(dsname);
                int i = 0;
                while (!file.EndOfStream)
                {
                    line = file.ReadLine();
                    i = i + 1;
                  
                }
                file.Close();
            }
            
            WMIrapport x = new WMIrapport();
            return x;
        }
    }
}
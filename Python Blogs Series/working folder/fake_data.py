f'''
        data {target_caslib}.loans_raw(drop=Date initialCurrentCategories CurrentCategories ) /*accounts*/
             {target_caslib}.customers(keep=CurrentCategories ID Salary Date Age EmpLength); /*customer info */
            call streaminit(99);
            length ID varchar(30)
                   AccNumber varchar(30)
                   Year 8.
                   Month 8.
                   Day 8.
                   CurrentDate varchar(9)
                   SalaryGroup varchar(22) 
                   Age 8.
                   Salary 8.
                   EmpLength 8.
                   Category varchar(16)
                   Amount 8.
                   InterestRate 8.
                   LoanLength 8.
                   initialCurrentCategories varchar(150)
                   CurrentCategories varchar(150)
                   LoanGrade varchar(1)
                   LoanStatus varchar(10)
                   LastPurchase 8.
                   Cancelled 8.
                   CancelledReason varchar(13)
            ;
            retain initialCurrentCategories "" 
                   LoanGrade "";

            ******************************************;
            * 1. Set the beginning year for the data *;
            ******************************************;
            YearStart=2013;

            ****************************************************;
            * 2. Set the current date for consistency: DEC2022 *;
            ****************************************************;
            * Make character *;
            CurrentDate=put(mdy(12,31,YearStart+9),date9.);

            **********************************************************;
            * 3. Start Loop to Create Rows For N Customers by thread *;
            **********************************************************;
            * Modify this value for more customers *;
                do i=1 to {number_of_customers_per_worker};

                    *******************;
                    * 3a.Set Cust ID  *;
                    *******************;
                    * Create random customer ID *;
                    array rand_letter[10] varchar(1) _temporary_ ('A','B','C','D','E','F','G','H','I','J');
                    randLetter=rand('table',.1,.1,.1,.1,.1,.1,.1,.1,.1,.1);
                    ID=catx('-',rand_letter[randLetter],put(rand('uniform',0,9999999999999999),z20.));

                    *******************************************************************;
                    * 3b. Set Salary Group, Salary, Emp Length, # of Accounts and Age *;
                    *******************************************************************;
                    * Create the Salary groups *;
                    array salary_group[5] varchar(22) _temporary_ ("Less than $50,000",      /*1*/
                                                                   "$50,001 - $100,000",     /*2*/
                                                                   "$100,001 - $250,000",    /*3*/
                                                                   "$250,001-$500,000",      /*4*/
                                                                   "Greater than $500,001"); /*5*/
                    
                    * Set probabilities for Salary Group *;
                    randSalGroup=rand("table",.22,.38,.29,.09,.02);
                    SalaryGroup=salary_group[randSalGroup];     

                    * Set salaries and number of accounts based off salary group *;
                    if SalaryGroup=salary_group[1] then do;
                        Salary=rand("uniform",10000,50000);
                        randAccounts=round(rand('uniform', 1,3));
                        Age=round(rand('uniform',18,50));
                    end;
                    else if SalaryGroup=salary_group[2] then do;
                        Salary=rand("uniform",50000,100000);
                        randAccounts=round(rand('uniform', 1,3));
                        Age=round(rand('uniform',22,60));
                    end;
                    else if SalaryGroup=salary_group[3] then do;
                        Salary=rand("uniform",100000,250000);
                        randAccounts=round(rand('uniform',1,4));
                        Age=round(rand('uniform',25,65));
                    end;
                    else if SalaryGroup=salary_group[4] then do;
                        Salary=rand("uniform",250000,500000);
                        randAccounts=round(rand('uniform', 1,5));
                        Age=round(rand('uniform',30,70));
                    end;
                    else if SalaryGroup=salary_group[5] then do;
                        Salary=rand("uniform",500000,2500000);
                        randAccounts=round(rand('uniform', 1,6));
                        Age=round(rand('uniform',40,70));
                    end;
                    else do;
                        Salary=rand('PARETO', 5, 3)*500000;
                        randAccounts=round(rand('PARETO', 6,2));
                        Age=round(rand('uniform',45,70));
                    end;
					if Age < 20 then Salary=Salary * .25;
				    else if Age < 25 then Salary=Salary * .4;
					else if Age < 30 then Salary=Salary * .6;
			    	else if age < 40 then Salary=Salary * .7;
					else if Age > 65 then Salary=Salary * .9;

                    * Set Random number for Employed Length Years *;
                    EmpLength=ceil(rand('normal',11,4.5));
                    if EmpLength < 0 then EmpLength=.;
                   
*****************************************************************************************************************;
                    ***************************************************************;
                    * 4. Create Loop for Multiple Different Accounts Per Customer *;
                    ***************************************************************;
                    * Reset loan grade after each new customer prior to the below loop for each account*;
                    LoanGrade="";

                    do i_numAccounts=1 to randAccounts;
              

                    *Reset variables *;
                    * Reset last purchase of CC date and promotion *;
                    LastPurchase=.;
                    Promotion=0;


                    ***********************************;
                    * 5. Create Dates(Year,Month,Day) *;
                    ***********************************;
                    array Year_values[10]  _temporary_ (0,1,2,3,4,5,6,7,8,9);                    
                    randYear=rand('table',.02,.04,.06,.07,.1,.13,.15,.11,.14,.18);
                    Year=YearStart + Year_values[randYear];
                    Month=round(rand('uniform', 1, 12));
                    Day=round(rand('uniform',1,27));
                    Date=mdy(Month,Day, Year);
                    

                    ***************************;
                    * 6. Create loan Category *;
                    ***************************;
                    array category_group[13] varchar(16) _temporary_ ("Credit Card",     /*1*/
                                                               "Consolidation",   /*2*/
                                                               "Mortgage",        /*3*/
                                                               "Home Improvement",/*4*/
                                                               "Car Loan",        /*5*/
                                                               "Personal",        /*6*/
                                                               "Moving Expenses", /*7*/
                                                               "Small Business",  /*8*/
                                                               "Vacation",        /*9*/
                                                               "Medical",         /*10*/
                                                               "Major Purchase",  /*11*/
                                                               "Weddings",        /*12*/
                                                               "Education");      /*13*/
                   randCategory=rand("table",.52    /* 1.Credit Card */
                                     ,.09    /* 2.Consolidation */
                                     ,.08    /* 3.Mortgage */
                                     ,.06    /* 4.Home Improvement */
                                     ,.07    /* 5.Car Loan */
                                     ,.01    /* 6.Personal */
                                     ,.005   /* 7.Moving Expenses */
                                     ,.07    /* 8.Small Business */
                                     ,.01    /* 9.Vacation */
                                     ,.03    /* 10.Medical */
                                     ,.01    /* 11.Major Purchase */
                                     ,.005   /* 12.Weddings */
                                     ,.06);  /* 13.Education */
                   Category=category_group[randCategory];

                   *************************************;
                   * 7. Fix any issues with Categories *; 
                   *************************************;
                   *like someone with 50k having multiple mortgages or consolidations *;
                   
                   * Create a string will initial categories*;
                   initialCurrentCategories=catx(",",initialCurrentCategories,Category);
                   * Create random variable value. Use as pct chance *;
                   randChance=rand("uniform",0,1);

                   /* People with less than 50K have a small small chance of two mortgages (3%) or multiple consolidations (1%) */
                   if SalaryGroup=salary_group[1] then do;                        
                        if count(initialCurrentCategories,"Mortgage") = 2 and (randChance < .97) then Category="Credit Card";
                        if count(initialCurrentCategories,"Consolidation") = 2 and (randChance < .99) then Category="Credit Card";
                   end;
                   /* People with 50-100K have a small chance of two mortgages (5%) or multiple consolidations (3%) */
                   else if SalaryGroup=salary_group[2] then do;
                        if count(initialCurrentCategories,"Mortgage") = 2 and (randChance < 95) then Category="Credit Card";
                        if count(initialCurrentCategories,"Consolidation") = 2 and (randChance < .97) then Category="Credit Card";
                   end;
                   /* People with 100K-250K have a chance of two + mortgages (12%) or multiple consolidations (5%) */
                   else if SalaryGroup=salary_group[3] then do;
                        randChance=rand("uniform",0,1);
                        if count(initialCurrentCategories,"Mortgage") >= 2 and (randChance < .88) then Category="Credit Card";
                        if count(initialCurrentCategories,"Consolidation") >= 2 and (randChance < .95) then Category="Credit Card";
                   end;
    
                   * Create a string will UPDATED categories*;
                   CurrentCategories=catx(",",CurrentCategories,Category);

                   ********************************************;
                   * 8. Create Account Numbers for Categories *; 
                   ********************************************;
                   if Category="Credit Card" then AccNumber=catx("-","PKEO",put(rand("uniform",1,9999),z4.),put(rand("uniform",1,9999),z4.),put(rand("uniform",1,9999),z4.),put(rand("uniform",1,9999),z4.));
                   else if Category="Consolidation" then AccNumber=cats("CL",put(rand("uniform",1,9999999999999999),z16.),put(rand("uniform",1,99999),z5.),substr(ID,3,5));
                   else if Category="Mortgage" then AccNumber=cats("M",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,3));
                   else if Category="Home Improvement" then AccNumber=cats("HI",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Car Loan" then AccNumber=cats("CL",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Personal" then AccNumber=cats("PE",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Moving Expenses" then AccNumber=cats("MV",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Small Business" then AccNumber=cats("SB",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Vacation" then AccNumber=cats("VA",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));                  
                   else if Category="Medical" then AccNumber=cats("MD",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Major Purchase" then AccNumber=cats("MJ",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Weddings" then AccNumber=cats("W",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else if Category="Education" then AccNumber=cats("E",put(rand("uniform",1,9999999999999999),z16.),"-",put(rand("uniform",1,99999),z5.),substr(ID,3,2));
                   else AccNumber="";

                ******************************************************;
                * 9. Create Loan Amount, Loan Length, Interest Rate *; 
                ******************************************************;

                   *******************************************************************************;
                   * 9a. Personal, Vacation, Home Improvement, Weddings, Major Purchase, Moving *;
                   *******************************************************************************;
                   array length_groups1[3] _temporary_ (2,3,5);
                   if Category in ("Personal", "Vacation", "Home Improvement", "Weddings", "Major Purchase", "Moving Expenses") then do;
                        * Amount *;
                        if Salary < 250000 then Amount=rand("pareto",4)*4000; 
                        else if Salary < 750000 then Amount=rand("pareto",3,1.5)*5000;
                        else Amount=rand("pareto",3,2)*10000;
                        
                        * Length *;
                        LoanLength=length_groups1[rand("table",.24,.40,.36)];
                        
                        * Interst rate *;
                        randHomeImprovement=rand('uniform',0,1);
                        if Category="Home Improvement" and randHomeImprovement < .30 then do;
                            InterestRate=0;
                            Promotion=1;
                            LoanLength=1.5;
                        end;
                        else do;
                            InterestRate=rand("normal",15,2.5);
                            Promotion=0;
                        end;
                   end;
                   ****************************************;
                   * 9b. Consolidation + Small Business  *;
                   ****************************************;
                   * Consolidation + Small Business*;
                   else if Category in ('Consolidation', 'Small Business') then do;
                        * Set amount *;
                        Amount=rand('EXTRVALUE', Salary/15, Salary/10); 
                        
                        * Change all amounts under 3500 *;
                        if Amount <1500 then Amount=rand('uniform',3500,10000);
                        
                        * Set loan length *;
                        array length_consol[3] _temporary_ (5,7,10);
                        LoanLength=length_consol[rand('table',.20,.35,.45)];

                        * Interst rate *;
                        if Category='Consolidation' then InterestRate=rand('normal',7.5,1);
                        else InterestRate=rand('normal',10,2.5);
                   end;

                   *********************;
                   * 9c. Car Loans    *;
                   *********************;
                   else if Category="Car Loan" then do;
                        * Set amount *;
                        if Salary < 50000 then Amount=rand('normal', 17000,3500);
                        else if Salary < 200000 then Amount=rand('normal', 35000,7500);
                        else if Salary < 500000 then Amount=rand('normal', 45000,10000);
                        else Amount=rand('normal', 60000,10000);
                        
                        * Set loan length *;
                        array length_car[4] _temporary_ (2,3,5,7);
                        LoanLength=length_car[rand("table",.02,.06,.6,.32)];

                        * Interst rate *;
                        InterestRate=rand('normal',5.25,1);
                   end;

                   *********************************;
                   * 9d. Education and Medical    *;
                   *********************************;
                   else if Category in ("Education","Medical") then do;
                        * Set amount *;
                        Amount=rand("normal",40000,7500);
                        if Salary > 250000 and Category="Education" then Amount=Amount + 10000;
                        
                        * Set length *;
                        if Category="Education" then LoanLength=10;
                            else LoanLength=5;

                        * Interst rate *;
                        if Category="Education" then InterestRate=rand('normal',7,1);
                        else InterestRate=rand('normal',8,.5);            
                   end;

                   *********************************;
                   * 9e. Mortgage                 *;
                   *********************************;
                   else if Category="Mortgage" then do;
                        * Set amount *;
						randMortgageAmt = rand('uniform',0,1);
						if randMortgageAmt < .15 then Amount=rand('normal', Salary*2, Salary/4);
							else if randMortgageAmt < .35 then Amount=rand('normal', Salary*2.25, Salary/4);
							else if randMortgageAmt < .75 then Amount=rand('normal', Salary*2.5, Salary/4);
							else if randMortgageAmt < .9 then Amount=rand('normal', Salary*2.75, Salary/4);
							else Amount=rand('normal', Salary*3, Salary/4);
                        
						* Random increase mortgages by 2 *;
                        randIncMort=rand('uniform',0,1);
                        if randIncMort < .10 then Amount=Amount * 1.25;

                        * Set loan length *;
                        array length_mort[4] _temporary_ (10,15,20,30);
                        LoanLength=length_mort[rand('table',.05,.09,.12,.74)];
                        InterestRate=rand('normal',4.5,.5);
                   end;

                   *********************************;
                   * 9f. Credit Card              *;
                   *********************************;
                   else if Category="Credit Card" then do;

                       * Loan length - no length. Default is 999999 *;
                       LoanLength=999999;

                       * Set amount ;
                       Amount=rand('normal', 7000, 3250);

                       * Modify Amounts negative and small amounts *;
                       if Amount < 2.05 then Amount=rand('uniform',2.05,2000);  

                       * Randomly increase CC amount *;
                       randCCIncrease=rand('uniform', 0,1);
                       if (randCCIncrease > .1 and randCCIncrease < .15 and Salary > 100000) then Amount=Amount * rand('uniform',1,2.5);

                       * Last CC Purchase date *;
                       accountOpenDate=mdy(Month,Day,Year);
                       CurrDateNum=input(CurrentDate, date9.); * make text number for current date to use in formulas ;

                       * Most of the last purchases are for the current month. *;
                       randLastPurchase=rand('uniform',0,1);
                       if randLastPurchase < .70 then do;
                            LastPurchase=int(rand('uniform', mdy(12,rand('uniform',1,31),year(currDateNum)), CurrDateNum));
                            if Amount=0 and randCCINcrease > .7 then Amount=Amount=rand('normal', 2000, 400);
                       end;
                       * The remaining minority have a random date *;
                       else do;
                             LastPurchase=int(rand('uniform', accountOpenDate, CurrDateNum));
                       end;
                       
                       * Credit Card interest rate.  *;
                       * Majority of cards have an interest rate *;
                       * Some cards in the current year have a promo 0% interest *;
                       randCCPromo=rand('uniform',0,1);
                       if Year ne Year+9 then do;
                            InterestRate=rand('normal',19,2);
                       end;
                       else if randCCPromo > .25 then do;
                            InterestRate=rand('normal',19,2);
                       end;
                       else do;
                            InterestRate=0;
                            Promotion=1;
                       end;

                   end;
                   else do;
                        Amount=.;
                   end;


                   **************************************;
                   * 10. Set Loan Grade based on Salary *;
                   **************************************; 
                   * Only set on first iteration of loop. Reset at top of the loop *;
                   array loan_grade[5] varchar(1) _temporary_ ('A','B','C','D','E');
       
                   if i_numAccounts=1 then do;
                       if SalaryGroup=salary_group[1] then do;
                           LoanGrade=loan_grade[rand("table", .33, .27, .17, .13, .10)];
                       end;
                       else if SalaryGroup=salary_group[2] then do;
                           LoanGrade=loan_grade[rand("table", .38, .29, .16, .11, .06)];
                       end;
                       else if SalaryGroup=salary_group[3] then do;
                           LoanGrade=loan_grade[rand("table", .42, .30, .13, .10, .05)];
                       end;
                       else if SalaryGroup=salary_group[4] then do;
                           LoanGrade=loan_grade[rand("table", .46, .34, .10, .07, .03)];
                       end;
                       else if SalaryGroup=salary_group[5] then do;
                           LoanGrade=loan_grade[rand("table", .51, .37, .07, .04, .01)];
                       end;
                       else do;
                           LoanGrade=loan_grade[rand("table", .555, .40, .03, .01, .005)];
                       end;
                   end;


                   ************************************;
                   * 11. LoanStatus + Modify Amounts  *;
                   ************************************;
                   array Loan_Status[5] varchar(10) _temporary_ ('Fully Paid','Current','Late','Default', 'Charged Off');
                   
                    * Check to see if the length of the loan is complete by comparing CurrentYear to Year started
                    Greater than 0 means the loan date is complete *;
                   if Category ne 'Credit Card' then Year_Minus_Loan_Term=(year(CurrDateNum)-Year)-LoanLength;                   
                   else Year_Minus_Loan_Term = .;


                   * Set loan status for all loans *;

                   * Loan status for CC with a last purchase 1 years ago*;
                   if Category = 'Credit Card' then do;
                        randCCLoanStatus=rand('uniform',0,1);

                        * If the last CC purchase is greater than 1 year out *;
                        if Year(CurrDateNum) - Year(LastPurchase) > 1 then do;
                           * Most loans are fully paid *;
                           if randCCLoanStatus < .8 then do;
                                Amount=0;
                                LoanStatus=Loan_Status[1];
                           end;
                           * Some loans are current *;
                           else if randCCLoanStatus < .87 then do;
                                LoanStatus=Loan_Status[2];
                           end;
                           * Some loans are Late *;
                           else if randCCLoanStatus < .92 then do;
                                LoanStatus=Loan_Status[3];
                                if Amount < 500 then Amount=rand('uniform', 500, 10000);
                           end;
                           * Some loans are Default *;
                           else if randCCLoanStatus < .97 then do;
                                LoanStatus=Loan_Status[4];
                                if Amount < 500 then Amount=rand('uniform', 500, 10000);
                           end;
                           * Some loans are Charged off *;
                           else do;
                                LoanStatus=Loan_Status[5];
                                if Amount < 500 then Amount=rand('uniform', 500, 10000);
                           end;
                        end;

                        * CC accounts with a purchase within 1 year *;
                        else do;
                           * Most loans are  current *;
                           if randCCLoanStatus < .15 then do;
                                Amount=0;
                                LoanStatus=Loan_Status[1];
                           end;
                           * Some loans are current *;
                           else if randCCLoanStatus < .90 then do;
                                LoanStatus=Loan_Status[2];
                           end;
                           * Some loans are Late *;
                           else if randCCLoanStatus < .97 then do;
                                LoanStatus=Loan_Status[3];
                           end;
                           * Some loans are Default *;
                           else if randCCLoanStatus < .995 then do;
                                LoanStatus=Loan_Status[4];
                                if Amount < 500 then Amount=rand('uniform', 500, 10000);
                           end;
                           * Some loans are Charged off *;
                           else do;
                                LoanStatus=Loan_Status[5];
                                if Amount < 500 then Amount=rand('uniform', 500, 10000);
                           end;
                        end;
                   end;

                   * Loan status for all other categories *;
                   *('Fully Paid','Current','Late','Default', 'Charged Off');
                   else do;
                        *If current date does not exceed loan length. Make most loans current *;
                        if Year_Minus_Loan_Term < 0 then do;
                            randLoanStatusPct=rand('table',.05,.86,.04,.03,.02); 
                            LoanStatus=Loan_Status[randLoanStatusPct];
                        end;
                        * If loan length is complete, make most fully paid*;
                        else do;
                            randLoanStatusPct=rand('table',.88,.05,.04,.02,.01); 
                            LoanStatus=Loan_Status[randLoanStatusPct];
                        end;
                   end;


                   **************************;
                   * 12. Cancelled Accounts *;
                   **************************;  
                   * Make a small number of accounts cancelled. Truncate one of the values *;
                   array cancelledReasons[7] varchar(13) _temporary_ ('Bad Service', 
                                                              'No Longer Needed', 
                                                              'Transfer', 
                                                              'Better Alternative',
                                                              'No Reason',
                                                              'Other',
                                                              ''); 

				   * Add cancelled loans *;
                   if rand('uniform',0,1) < .99 then do;
                     Cancelled=0;
                     CancelledReason="";
                   end;
                   else do;
                     Cancelled=1;
                     LoanStatus='Cancelled';
                     CancelledReason=cancelledReasons[rand('table',.15,.19,.10,.33,.06,.14,.03)];
                     * Cancelled credit card can't have a balance *;
                     if Category='Credit Card' then Amount=0;
                   end;



                   ******************************************************************;
                   * 13. Modify Interest Rates and Amounts by Year and Loan Grade   *;
                   ******************************************************************;
                   *Modify Interest Rate based on LoanGrade and Years for all non promos *;
                   if Promotion=0 then do;

                   *Modify interest rate for loan grades *;
                       if LoanGrade='A' then InterestRate=InterestRate*.85;
                            else if LoanGrade='B' then InterestRate=InterestRate*.95;
                            else if LoanGrade='C' then InterestRate=InterestRate*1.1;
                            else if LoanGrade='D' then InterestRate=InterestRate+1.25;
                            else  InterestRate=InterestRate+1.5;
    
                    *Modify interest rates and accounts for years *;
                       if Year < YearStart + 2 then do;
                            if InterestRate ne 0 then InterestRate=InterestRate * 1.15;
                            if Amount ne 0 then Amount=Amount*.6;
                       end;
                       else if Year < YearStart + 4 then do;
                            if InterestRate ne 0 then InterestRate=InterestRate * 1.03;
                            if Amount ne 0 then Amount=Amount*.65;
                       end;
                       else if Year < YearStart + 6 then do;
                            if InterestRate ne 0 then InterestRate=InterestRate * .97;
                            if Amount ne 0 then Amount=Amount*.85;
                       end;
                       else if Year < YearStart + 8 then do;
                            if InterestRate ne 0 then InterestRate=InterestRate * .90;
                            if Amount ne 0 then Amount=Amount*.95;
                       end;
                       else do;
                            if InterestRate ne 0 then InterestRate=InterestRate *.85;
                            if Amount ne 0 then Amount=Amount*1.05;
                       end;  

                   end;

                   ******************************************************************************************;
                   * 14. Modify Loan Status for Credit Cards and Mortgage. Increase late, default, charge   *;
                   ******************************************************************************************;
                   randCCLoanStatus=rand('uniform',0,1);
                   if randCCLoanStatus < .05 and Category='Credit Card' then LoanStatus=Loan_Status[rand('table',0,0,.5,.35,.15)];
                      else if randCCLoanStatus > .95 and Category='Mortgage' then LoanStatus=Loan_Status[rand('table',0,0,.6,.35,.05)];
                        

                   ********************************;             
                   * 15. Round/fix numeric values *;
                   ********************************;
				   * Fix any negative values *;
				   if Amount < 0 then Amount = Amount * (-1);
				   if InterestRate < 0 then InterestRate=InterestRate * (-1);

				   * Round values *;
                   Amount=round(Amount,.01);
                   Salary=round(Salary);
                   InterestRate=round(InterestRate,.01); 


                   ****************************;             
                   * 16. Random Breaking Data *;
                   ****************************;
                   * Make .00001 of Amounts negative for 'refunds' *;
                   randBreak=rand('uniform',0,1);
                   if (Category = 'Credit Card') and (randBreak < .00001) then Amount=round(rand('Uniform',1,3000),.01) * (-1);


                   **********************************;
                   * 17. Output to loan_raw table   *;
                   **********************************;
                  * Output to loans raw for each customer and all accounts *;  
                   output {target_caslib}.loans_raw;

                   ******************************;
                   * 18. END LOOP Account Loop  *;
                   ******************************;
                   * ends the loop for creating values for each user's account *;   
                   end;


            ***************************************;
            * 17. End Main Loop (customerID loop) *;
            ***************************************;
            * Outputs the last row created for the customer to the customers table *;
            output {target_caslib}.customers;

            *************************************;
            * 18. Reset current categories list *;
            *************************************;
            * Reset the lists that hold each category of loan that customers has *;
            initialCurrentCategories="";
            CurrentCategories="";
            end;

            drop i i_numAccounts rand: YearStart accountOpenDate  Year_Minus_Loan_Term CurrDateNum;
            format LastPurchase date9.;
        run;

    endsource;
'''
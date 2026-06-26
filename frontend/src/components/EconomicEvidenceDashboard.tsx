import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface EconomicIndicator {
  id: number;
  date: string;
  indicator_type: string;
  value: number;
  source: string;
  region: string;
}

interface PolicyAction {
  id: number;
  date: string;
  policy_type: string;
  policy_name: string;
  description: string;
  claimed_purpose: string;
  actual_impact: string;
  affected_groups: string;
}

interface WealthTransfer {
  id: number;
  date: string;
  mechanism: string;
  amount: number;
  from_group: string;
  to_group: string;
  method: string;
  evidence_summary: string;
}

interface HistoricalParallel {
  historical_regime: string;
  mechanism: string;
  historical_policy: string;
  description: string;
  current_parallel: {
    policy: string;
    mechanism: string;
    similarity: string;
  };
}

const EconomicEvidenceDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wealthGapData, setWealthGapData] = useState<any>(null);
  const [historicalParallels, setHistoricalParallels] = useState<HistoricalParallel[]>([]);
  const [transparencyOverview, setTransparencyOverview] = useState<any>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch wealth gap analysis
      const wealthGapResponse = await fetch(`${API_BASE_URL}/wealth-gap/policy-impact-analysis`);
      const wealthGapData = await wealthGapResponse.json();
      setWealthGapData(wealthGapData);

      // Fetch historical parallels
      const parallelsResponse = await fetch(`${API_BASE_URL}/historical-parallels/oppression-mechanisms`);
      const parallelsData = await parallelsResponse.json();
      setHistoricalParallels(parallelsData.historical_parallels || []);

      // Fetch transparency campaign overview
      const transparencyResponse = await fetch(`${API_BASE_URL}/transparency/campaign-overview`);
      const transparencyData = await transparencyResponse.json();
      setTransparencyOverview(transparencyData);

    } catch (err) {
      setError('Failed to fetch economic evidence data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading economic evidence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <button 
          onClick={fetchData}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Economic Evidence Dashboard
        </h1>
        <p className="text-xl text-gray-600">
          Tracking government accountability and wealth transfer mechanisms
        </p>
      </div>

      {/* Risk Assessment Alert */}
      <Alert className="border-red-200 bg-red-50">
        <AlertDescription className="text-red-800">
          <strong>Risk Assessment:</strong> Historical parallels analysis indicates {historicalParallels.length} 
          concerning similarities between current Canadian policies and historical authoritarian regimes. 
          Warning level: <span className="font-bold">HIGH</span>
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="wealth-gap" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="wealth-gap">Wealth Gap Analysis</TabsTrigger>
          <TabsTrigger value="historical">Historical Parallels</TabsTrigger>
          <TabsTrigger value="transparency">Transparency Campaign</TabsTrigger>
          <TabsTrigger value="evidence">Evidence Collection</TabsTrigger>
        </TabsList>

        {/* Wealth Gap Analysis Tab */}
        <TabsContent value="wealth-gap" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Policy Impact Analysis</CardTitle>
                <CardDescription>Policies affecting wealth distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {wealthGapData?.total_policies_analyzed || 0}
                </div>
                <p className="text-sm text-gray-600">Policies analyzed</p>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between">
                    <span>Wealth widening:</span>
                    <span className="text-red-600 font-semibold">
                      {wealthGapData?.widening_policies || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Wealth narrowing:</span>
                    <span className="text-green-600 font-semibold">
                      {wealthGapData?.narrowing_policies || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Wealth Transfer Totals</CardTitle>
                <CardDescription>Documented wealth transfers</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {formatCurrency(wealthGapData?.total_transferred || 0)}
                </div>
                <p className="text-sm text-gray-600">Total transferred</p>
                <div className="mt-4">
                  <Badge variant="outline" className="mb-2">
                    {wealthGapData?.transfer_count || 0} transfers documented
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Business Performance Gap</CardTitle>
                <CardDescription>Small business vs corporate</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Profit margin gap:</span>
                    <span className="text-red-600 font-semibold">
                      {wealthGapData?.performance_gap?.profit_margin_gap?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Growth rate gap:</span>
                    <span className="text-red-600 font-semibold">
                      {wealthGapData?.performance_gap?.growth_rate_gap?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Closure rate diff:</span>
                    <span className="text-red-600 font-semibold">
                      {wealthGapData?.performance_gap?.closure_rate_diff?.toFixed(1) || 0}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Historical Parallels Tab */}
        <TabsContent value="historical" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {historicalParallels.map((parallel, index) => (
              <Card key={index} className="border-red-200">
                <CardHeader>
                  <CardTitle className="text-lg text-red-800">
                    {parallel.historical_regime}
                  </CardTitle>
                  <CardDescription className="text-red-600">
                    {parallel.mechanism}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-700">Historical Policy:</h4>
                    <p className="text-sm text-gray-600">{parallel.historical_policy}</p>
                    <p className="text-sm text-gray-500 mt-1">{parallel.description}</p>
                  </div>
                  
                  <div className="border-t pt-4">
                    <h4 className="font-semibold text-gray-700">Current Parallel:</h4>
                    <p className="text-sm text-gray-600">{parallel.current_parallel.policy}</p>
                    <p className="text-sm text-gray-500 mt-1">{parallel.current_parallel.similarity}</p>
                  </div>
                  
                  <Badge variant="destructive">
                    High Similarity
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Transparency Campaign Tab */}
        <TabsContent value="transparency" className="space-y-6">
          {transparencyOverview && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Emergency Powers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">
                    {transparencyOverview.campaign_tracks?.emergency_powers?.total_records || 0}
                  </div>
                  <p className="text-sm text-gray-600">Powers documented</p>
                  <div className="mt-2">
                    <Badge variant="destructive">
                      {transparencyOverview.campaign_tracks?.emergency_powers?.no_oversight || 0} with no oversight
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Surveillance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">
                    {transparencyOverview.campaign_tracks?.surveillance_infrastructure?.total_records || 0}
                  </div>
                  <p className="text-sm text-gray-600">Programs tracked</p>
                  <div className="mt-2">
                    <Badge variant="outline">
                      {formatCurrency(transparencyOverview.campaign_tracks?.surveillance_infrastructure?.total_budget || 0)} budget
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Financial Transparency</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-yellow-600">
                    {transparencyOverview.campaign_tracks?.financial_transparency?.total_records || 0}
                  </div>
                  <p className="text-sm text-gray-600">Operations documented</p>
                  <div className="mt-2">
                    <Badge variant="outline">
                      {transparencyOverview.campaign_tracks?.financial_transparency?.low_transparency || 0} low transparency
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Civil Liberties</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-600">
                    {transparencyOverview.campaign_tracks?.civil_liberties_litigation?.total_records || 0}
                  </div>
                  <p className="text-sm text-gray-600">Legal challenges</p>
                  <div className="mt-2">
                    <Badge variant="outline">
                      {transparencyOverview.campaign_tracks?.civil_liberties_litigation?.victory_rate?.toFixed(1) || 0}% success rate
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Overall Assessment */}
          {transparencyOverview && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="text-xl text-red-800">Overall Assessment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-700">Total Evidence Items</h4>
                    <p className="text-2xl font-bold text-red-600">
                      {transparencyOverview.overall_assessment?.total_evidence_items || 0}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-700">Accountability Concerns</h4>
                    <Badge className={getRiskLevelColor(transparencyOverview.overall_assessment?.accountability_concerns || 'high')}>
                      {transparencyOverview.overall_assessment?.accountability_concerns?.toUpperCase() || 'HIGH'}
                    </Badge>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-700">Citizen Risk Level</h4>
                    <Badge className={getRiskLevelColor(transparencyOverview.overall_assessment?.citizen_risk_level || 'elevated')}>
                      {transparencyOverview.overall_assessment?.citizen_risk_level?.toUpperCase() || 'ELEVATED'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Evidence Collection Tab */}
        <TabsContent value="evidence" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Small Business Evidence</CardTitle>
                <CardDescription>Documenting small business destruction patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-red-50 rounded border border-red-200">
                    <h4 className="font-semibold text-red-800">2022-2024 Scenario</h4>
                    <p className="text-sm text-gray-700 mt-2">
                      • 2022: Good sales, good profits<br/>
                      • 2023: More sales, same profits (inflation eating margins)<br/>
                      • 2024: Even more sales, lower profits (getting squeezed)
                    </p>
                  </div>
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Add Business Metrics
                  </button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Government Hypocrisy</CardTitle>
                <CardDescription>Statements vs. harmful actions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-orange-50 rounded border border-orange-200">
                    <h4 className="font-semibold text-orange-800">Recent Examples</h4>
                    <p className="text-sm text-gray-700 mt-2">
                      "We're doing everything we can to help Canadians"<br/>
                      vs. Policies destroying small businesses and reducing purchasing power
                    </p>
                  </div>
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Document Hypocrisy
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Evidence Collection Tools</CardTitle>
              <CardDescription>API endpoints for data collection</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="p-4 bg-gray-50 rounded border hover:bg-gray-100">
                  <h4 className="font-semibold">Economic Indicators</h4>
                  <p className="text-sm text-gray-600 mt-1">Add inflation, wealth gap data</p>
                </button>
                <button className="p-4 bg-gray-50 rounded border hover:bg-gray-100">
                  <h4 className="font-semibold">Policy Actions</h4>
                  <p className="text-sm text-gray-600 mt-1">Document government policies</p>
                </button>
                <button className="p-4 bg-gray-50 rounded border hover:bg-gray-100">
                  <h4 className="font-semibold">Wealth Transfers</h4>
                  <p className="text-sm text-gray-600 mt-1">Track wealth movement</p>
                </button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EconomicEvidenceDashboard;
